import csv
import datetime
import json
import logging
import os
from io import StringIO

from aka.utils import AKAJSONEncoder, gettext_lang, omit, send_mail
from django.conf import settings
from django.forms import formset_factory
from django.template.response import TemplateResponse
from django.views.generic.edit import FormView
from extra_views import FormSetView
from project.view_mixins import IsContentMixin, PdfRendererMixin
from udbytte.forms import UdbytteForm, UdbytteFormItem
from udbytte.models import U1A, U1AItem

logger = logging.getLogger(__name__)


class UdbytteView(IsContentMixin, PdfRendererMixin, FormSetView, FormView):
    form_class = UdbytteForm
    template_name = "udbytte/form.html"
    pdf_template_name = "udbytte/form.html"
    pdf_css_files = ["css/pdf.css"]

    factory_kwargs = {
        "extra": 1,
        "max_num": None,
        "can_order": False,
        "can_delete": True,
    }

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **{**kwargs, "u1_url_wrapped": json.dumps({"url": settings.TAX_FORM_U1})}
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if "initial" not in kwargs:
            kwargs["initial"] = {}
        kwargs["initial"] = {
            "dato": datetime.date.today().strftime("%d/%m/%Y"),
        }
        return kwargs

    def get_formset(self):
        return formset_factory(UdbytteFormItem, **self.get_factory_kwargs())

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        formset = self.construct_formset()
        # Trigger form cleaning of both form and formset
        # This ensures that:
        # * we have cleaned_data for the cross-check in clean_with_formset, which validates data across both forms,
        # * all errors are collected for display in form_invalid, not just from the first form that fails
        form.full_clean()
        formset.full_clean()
        # compares data between form and formset, and adds any errors to form
        form.clean_with_formset(formset)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        oprettet_af_cpr = self.request.session["user_info"]["cpr"]

        # Persist the submittet U1A in the database
        new_u1a_model = U1A.objects.create(
            **{**form.cleaned_data, "oprettet_af_cpr": oprettet_af_cpr}
        )
        for subform in filter(lambda sf: sf.cleaned_data, formset):
            U1AItem.objects.create(
                **{**omit(subform.cleaned_data, "DELETE"), "u1a": new_u1a_model}
            )

        # PDF handling
        pdf_data = self.render_filled_form(form, formset)
        self.send_mail_to_submitter(
            form.cleaned_data["email"], pdf_data, form.cleaned_data
        )

        # CSV handling
        csv_data = self.get_csv(form, formset)
        self.save_data(form, formset, csv_data, pdf_data)
        self.send_mail_to_office(
            settings.EMAIL_OFFICE_RECIPIENT, csv_data, pdf_data, form.cleaned_data
        )

        return TemplateResponse(
            request=self.request,
            template="udbytte/success.html",
            context={},
            using=self.template_engine,
        )

    def render_filled_form(self, form, formset):
        self.is_pdf = True
        return self.render(
            context=self.get_context_data(form=form, formset=formset, pdf=True),
            wrap_in_response=False,
        )

    def get_csv(self, form, formset):
        # Payment Year;"Payer CVR (udbetaler)";"Recipient CPR (modtager)"; Amount
        csv_io = StringIO()
        writer = csv.writer(csv_io, delimiter=";")
        for subform in formset:
            if subform.cleaned_data:
                writer.writerow(
                    [
                        form.cleaned_data["regnskabsår"],
                        form.cleaned_data["cvr"],
                        subform.cleaned_data["cpr_cvr_tin"],
                        subform.cleaned_data["udbytte"],
                    ]
                )
        return csv_io.getvalue()

    def form_invalid(self, form, formset):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

    @staticmethod
    def send_mail_to_submitter(recipient, pdf_data, formdata):
        subject = " / ".join(
            [
                gettext_lang("kl", "udbytte.mail1.subject").format(
                    company_name=formdata["virksomhedsnavn"],
                    year=formdata["regnskabsår"],
                ),
                gettext_lang("da", "udbytte.mail1.subject").format(
                    company_name=formdata["virksomhedsnavn"],
                    year=formdata["regnskabsår"],
                ),
            ]
        )
        textbody = [gettext_lang("kl", "udbytte.mail1.textbody")]
        if not formdata["u1_udfyldt"]:
            textbody.append(
                gettext_lang("kl", "udbytte.mail1.textreminder").format(
                    url=settings.TAX_FORM_U1
                )
            )
        textbody.append(gettext_lang("da", "udbytte.mail1.textbody"))
        if not formdata["u1_udfyldt"]:
            textbody.append(
                gettext_lang("da", "udbytte.mail1.textreminder").format(
                    url=settings.TAX_FORM_U1
                )
            )

        htmlbody = ["<html><body>", gettext_lang("kl", "udbytte.mail1.htmlbody")]
        if not formdata["u1_udfyldt"]:
            htmlbody.append(
                gettext_lang("kl", "udbytte.mail1.htmlreminder").format(
                    url=settings.TAX_FORM_U1
                )
            )
        htmlbody.append(gettext_lang("da", "udbytte.mail1.htmlbody"))
        if not formdata["u1_udfyldt"]:
            htmlbody.append(
                gettext_lang("da", "udbytte.mail1.htmlreminder").format(
                    url=settings.TAX_FORM_U1
                )
            )
        htmlbody.append("</body></html>")

        send_mail(
            recipient=recipient,
            subject=subject,
            textbody="\n".join(textbody),
            htmlbody="\n".join(htmlbody),
            attachments=(("formulardata.pdf", pdf_data, "application/pdf"),),
        )

    @staticmethod
    def send_mail_to_office(recipient, csv_data, pdf_data, formdata):
        subject = " / ".join(
            [
                gettext_lang("kl", "udbytte.mail2.subject").format(
                    company_name=formdata["virksomhedsnavn"],
                    year=formdata["regnskabsår"],
                ),
                gettext_lang("da", "udbytte.mail2.subject").format(
                    company_name=formdata["virksomhedsnavn"],
                    year=formdata["regnskabsår"],
                ),
            ]
        )
        textbody = "\n\n".join(
            [
                gettext_lang("kl", "udbytte.mail2.textbody").format(
                    company_name=formdata["virksomhedsnavn"],
                    csv=csv_data,
                ),
                gettext_lang("da", "udbytte.mail2.textbody").format(
                    company_name=formdata["virksomhedsnavn"],
                    csv=csv_data,
                ),
            ]
        )
        htmlbody = (
            "<html><body><p>" + textbody.replace("\n", "<br/>") + "</body></html>"
        )
        send_mail(
            recipient=recipient,
            subject=subject,
            textbody=textbody,
            htmlbody=htmlbody,
            attachments=(("formulardata.pdf", pdf_data, "application/pdf"),),
        )

    @staticmethod
    def save_data(form, formset, csv_data, pdf_data):
        folder = f"{settings.TAX_FORM_STORAGE}/{form.cleaned_data['regnskabsår']}/{form.cleaned_data['dato']}/{form.cleaned_data['cvr']}"
        os.makedirs(folder, exist_ok=True)
        file_base_name = f"{datetime.datetime.now().isoformat()}"

        with open(f"{folder}/{file_base_name}.pdf", "wb") as file:
            file.write(pdf_data)

        data = {
            "form": form.cleaned_data,
            "formset": [subform.cleaned_data for subform in formset],
            "csv": csv_data,
        }
        with open(f"{folder}/{file_base_name}.json", "w") as file:
            file.write(json.dumps(data, indent=2, cls=AKAJSONEncoder))
