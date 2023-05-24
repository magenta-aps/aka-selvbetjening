import magic
from aka.utils import gettext_lang, send_mail
from django.conf import settings
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic import FormView, UpdateView
from obligatorisk_pension.forms import ObligatoriskPensionForm
from obligatorisk_pension.forms import SkatteårForm
from obligatorisk_pension.models import ObligatoriskPension
from project.view_mixins import HasUserMixin
from project.view_mixins import IsContentMixin


class ObligatoriskPensionSkatteårView(IsContentMixin, HasUserMixin, FormView):
    form_class = SkatteårForm
    template_name = "pension/skatteår.html"

    def form_valid(self, form):
        return redirect(
            reverse("obligatorisk_pension:create", args=[form.cleaned_data["skatteår"]])
        )


class ObligatoriskPensionCreateView(IsContentMixin, HasUserMixin, UpdateView):
    form_class = ObligatoriskPensionForm
    template_name = "pension/form.html"
    model = ObligatoriskPension

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return queryset.get(cpr=self.cpr, skatteår=self.kwargs["skatteår"])
        except self.model.DoesNotExist:
            return None

    def form_valid(self, form):
        pension_object = form.save(commit=False)
        pension_object.cpr = self.cpr
        pension_object.skatteår = self.kwargs["skatteår"]
        pension_object.save()
        form.save_m2m()
        self.send_mail_to_submitter(pension_object.email, pension_object)
        self.send_mail_to_office(settings.EMAIL_OFFICE_RECIPIENT, pension_object)
        return TemplateResponse(
            request=self.request,
            template="pension/success.html",
            context={},
            using=self.template_engine,
        )

    def send_mail_to_submitter(self, recipient, object):
        subject = " / ".join(
            [
                gettext_lang("kl", "obligatorisk_pension.mail1.subject"),
                gettext_lang("da", "obligatorisk_pension.mail1.subject"),
            ]
        )
        textbody = [
            gettext_lang("kl", "obligatorisk_pension.mail1.textbody"),
            gettext_lang("da", "obligatorisk_pension.mail1.textbody"),
        ]
        htmlbody = [
            "<html><body>",
            gettext_lang("kl", "obligatorisk_pension.mail1.htmlbody"),
            gettext_lang("da", "obligatorisk_pension.mail1.htmlbody"),
            "</body></html>",
        ]
        send_mail(
            recipient=recipient,
            subject=subject,
            textbody="\n".join(textbody),
            htmlbody="\n".join(htmlbody),
        )

    def send_mail_to_office(self, recipient, object):
        subject = " / ".join(
            [
                gettext_lang("kl", "obligatorisk_pension.mail2.subject"),
                gettext_lang("da", "obligatorisk_pension.mail2.subject"),
            ]
        )
        textbody = [
            gettext_lang("kl", "obligatorisk_pension.mail2.textbody"),
            gettext_lang("da", "obligatorisk_pension.mail2.textbody"),
        ]
        htmlbody = [
            "<html><body>",
            gettext_lang("kl", "obligatorisk_pension.mail2.htmlbody"),
            gettext_lang("da", "obligatorisk_pension.mail2.htmlbody"),
            "</body></html>",
        ]

        attachments = []
        for fileobject in object.filer.all():
            name = fileobject.fil.name
            data = fileobject.fil.read()
            mimetype = magic.from_buffer(data, mime=True)
            attachments.append((name, data, mimetype))

        send_mail(
            recipient=recipient,
            subject=subject,
            textbody="\n".join(textbody),
            htmlbody="\n".join(htmlbody),
            attachments=attachments,
        )
