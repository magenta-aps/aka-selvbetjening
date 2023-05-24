import magic
from aka.utils import gettext_lang, send_mail
from django.conf import settings
from django.template.response import TemplateResponse
from django.views.generic import CreateView
from obligatorisk_pension.forms import ObligatoriskPensionForm
from project.view_mixins import IsContentMixin
from project.view_mixins import HasUserMixin
from obligatorisk_pension.models import ObligatoriskPension


class ObligatoriskPensionCreateView(IsContentMixin, HasUserMixin, CreateView):
    form_class = ObligatoriskPensionForm
    template_name = "pension/form.html"
    model = ObligatoriskPension

    def form_valid(self, form):
        pension_object = form.save(commit=False)
        pension_object.cpr = self.cpr
        pension_object.save()
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
        for fileobject in object.files.all():
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
