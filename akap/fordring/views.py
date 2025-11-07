import json
import logging
import re
import uuid
from datetime import date

from aka.clients.prisme import Prisme, PrismeClaimRequest, PrismeException
from aka.data.fordringsgruppe import groups
from aka.utils import flatten
from aka.views import GetReceiptView
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.edit import FormView
from fordring.forms import InkassoCoDebitorFormSet, InkassoForm, InkassoUploadForm
from project.view_mixins import ErrorHandlerMixin, IsContentMixin, RequireCvrMixin

logger = logging.getLogger(__name__)


class InkassoSagView(ErrorHandlerMixin, RequireCvrMixin, IsContentMixin, FormView):
    form_class = InkassoForm
    template_name = "fordring/form.html"

    def get_formset(self):
        return InkassoCoDebitorFormSet(**self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **{
                **kwargs,
                "formset": self.get_formset(),
            }
        )

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        formset = self.get_formset()
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        return self.form_invalid(form, formset)

    @staticmethod
    def send_claim(claimant_id, form, codebtors, cpr, cvr):
        prisme = Prisme()
        if prisme.mock:
            return ["1234"]

        claim_type = form.cleaned_data["fordringstype"].split(".")

        claim = PrismeClaimRequest(
            claimant_id=claimant_id,
            cpr_cvr=form.cleaned_data.get("debitor"),
            external_claimant=form.cleaned_data.get("fordringshaver2"),
            claim_group_number=claim_type[0],
            claim_type=claim_type[1],
            child_cpr=form.cleaned_data.get("barns_cpr"),
            claim_ref=form.cleaned_data.get("ekstern_sagsnummer"),
            amount_balance=form.cleaned_data.get("hovedstol"),
            text=form.cleaned_data.get("hovedstol_posteringstekst"),
            created_by=form.cleaned_data.get("kontaktperson"),
            period_start=form.cleaned_data.get("periodestart"),
            period_end=form.cleaned_data.get("periodeslut"),
            due_date=form.cleaned_data.get("forfaldsdato"),
            founded_date=form.cleaned_data.get("betalingsdato"),
            obsolete_date=form.cleaned_data.get("foraeldelsesdato"),
            notes=form.cleaned_data.get("noter"),
            codebtors=codebtors,
            files=[file for name, file in form.files.items()],
        )
        prisme_replies = prisme.process_service(claim, "fordring", cpr, cvr)
        return [reply.rec_id for reply in prisme_replies]

    def form_valid(self, form, formset):
        if len(self.claimant_ids) == 0:
            form.add_error(None, _("login.error_no_claimants"))
            return self.form_invalid(form, formset)
        codebtors = []
        if formset:
            for subform in formset:
                cpr = subform.cleaned_data.get("cpr")
                cvr = subform.cleaned_data.get("cvr")
                if cpr is not None:
                    codebtors.append(cpr)
                elif cvr is not None:
                    codebtors.append(cvr)
        pdf_id = None
        try:
            rec_ids = InkassoSagView.send_claim(
                self.claimant_ids[0], form, codebtors, self.cpr, self.cvr
            )
            if rec_ids:
                pdf_id = InkassoSagView.store_pdf_context(
                    self.request.session,
                    self.cvr,
                    [{**form.cleaned_data, "rec_ids": rec_ids}],
                )
        except PrismeException as e:
            form.add_error(None, e.as_validationerror)
            return self.form_invalid(form, formset)

        return TemplateResponse(
            request=self.request,
            template="fordring/success.html",
            context={
                "rec_ids": rec_ids,
                "upload": False,
                "pdf_id": pdf_id,
            },
            using=self.template_engine,
        )

    def form_invalid(self, form, formset):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

    @staticmethod
    def store_pdf_context(session, cvr, data):
        now = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf_context = {
            "received_date": date.today(),
            "cvr": cvr,
            "lines": [
                {
                    "debitor": subdata.get("debitor"),
                    "fordringsgruppe": InkassoForm.get_group_name(
                        subdata.get("fordringsgruppe")
                    ),
                    "fordringstype": InkassoForm.get_group_type_text(
                        subdata.get("fordringstype")
                    ),
                    "ekstern_sagsnummer": subdata.get("ekstern_sagsnummer"),
                    "hovedstol": subdata.get("hovedstol"),
                    "forfaldsdato": subdata.get("forfaldsdato"),
                    "rec_ids": subdata["rec_ids"],
                }
                for subdata in data
            ],
        }
        if "receipts" not in session:
            session["receipts"] = {}
        pdf_id = str(uuid.uuid4())
        session["receipts"][pdf_id] = {
            "context": pdf_context,
            "filename": f"kvittering_fordring_{now}.pdf",
            "template": "fordring/receipt.html",
        }
        session.modified = True
        return pdf_id


class InkassoSagUploadView(
    RequireCvrMixin, ErrorHandlerMixin, IsContentMixin, FormView
):
    form_class = InkassoUploadForm
    template_name = "fordring/upload.html"
    parallel = False

    def handle_subform(self, subform):
        codebtor_re = re.compile(r"^codebtor_\d+$")
        claimant = subform.cleaned_data["fordringshaver"] or self.claimant_ids[0]
        codebtors = []
        for field, value in subform.cleaned_data.items():
            match = codebtor_re.match(field)
            if match and len(value):
                codebtors.append(value)
            if field == "meddebitorer" and len(value):
                codebtors += value.split(",")
        try:
            rec_ids = InkassoSagView.send_claim(
                claimant, subform, codebtors, self.cpr, self.cvr
            )
            return {**subform.cleaned_data, "rec_ids": rec_ids}
        except PrismeException as e:
            logger.exception(e)
            return {"error": e}

    def form_valid(self, form):
        if len(self.claimant_ids) == 0:
            form.add_error(
                None,
                ValidationError(
                    _("login.error_no_claimants"), "login.error_no_claimants"
                ),
            )
            return self.form_invalid(form)

        if self.parallel:
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                results = list(
                    executor.map(
                        self.handle_subform, [subform for subform in form.subforms]
                    )
                )
        else:
            results = [self.handle_subform(subform) for subform in form.subforms]

        responses = []
        errors = []
        for result in results:
            if "rec_ids" in result:
                responses.append(result)
            if "error" in result:
                errors.append(result["error"].as_error_dict)

        pdf_id = None
        if responses:
            pdf_id = InkassoSagView.store_pdf_context(
                self.request.session, self.cvr, responses
            )

        return TemplateResponse(
            request=self.request,
            template="fordring/success.html",
            context={
                "rec_ids": flatten([response["rec_ids"] for response in responses]),
                "upload": True,
                "errors": errors,
                "pdf_id": pdf_id,
            },
            using=self.template_engine,
        )


class FordringReceiptView(GetReceiptView):
    context = "fordring"


class InkassoGroupDataView(View):
    def get(self, request, var="", *args, **kwargs):
        data = json.dumps(groups)
        if var:
            return HttpResponse("%s = %s" % (var, data), content_type="text/javascript")
        return HttpResponse(data, content_type="application/json")
