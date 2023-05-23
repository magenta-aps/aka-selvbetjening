from django.template.response import TemplateResponse
from django.views.generic import FormView

from project.view_mixins import IsContentMixin
from obligatorisk_pension.forms import ObligatoriskPensionForm

from aka.utils import gettext_lang, send_mail


class ObligatoriskPensionView(IsContentMixin, FormView):
    form_class = ObligatoriskPensionForm
    template_name = "pension/form.html"

    def form_valid(self, form):
        object = form.save()
        self.send_mail_to_submitter(object.email, object)

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
