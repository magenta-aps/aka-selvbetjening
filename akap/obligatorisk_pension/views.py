import magic
from aka.utils import gettext_lang, send_mail
from django.conf import settings
from django.shortcuts import redirect
from django.template import Context, Engine
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic import FormView, UpdateView
from obligatorisk_pension.forms import ObligatoriskPensionForm, SkatteårForm
from obligatorisk_pension.models import ObligatoriskPension
from project.view_mixins import ErrorHandlerMixin, HasUserMixin, IsContentMixin


class ObligatoriskPensionSkatteårView(
    ErrorHandlerMixin, IsContentMixin, HasUserMixin, FormView
):
    form_class = SkatteårForm
    template_name = "pension/skatteår.html"

    def form_valid(self, form):
        return redirect(
            reverse("obligatorisk_pension:create", args=[form.cleaned_data["skatteår"]])
        )


class ObligatoriskPensionCreateView(
    ErrorHandlerMixin, IsContentMixin, HasUserMixin, UpdateView
):
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.person and not self.object:
            kwargs["initial"]["navn"] = self.person["navn"]
            kommunekode = self.person.get("myndighedskode", None)
            if kommunekode:
                kwargs["initial"]["kommune"] = kommunekode
        return kwargs

    def form_valid(self, form):
        pension_object = form.save(
            commit=True, cpr=self.cpr, skatteår=self.kwargs["skatteår"]
        )
        self.send_mail_to_submitter(pension_object.email, pension_object)
        self.send_mail_to_office(settings.EMAIL_OP_RECIPIENT, pension_object)
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
        engine = Engine.get_default()
        context = Context({"object": object})
        textbody = [
            engine.from_string(
                gettext_lang(lang, "obligatorisk_pension.mail1.textbody")
            ).render(context)
            for lang in ("kl", "da")
        ]
        htmlbody = (
            "<html><body>"
            + "<hr/>".join(
                [
                    engine.from_string(
                        gettext_lang(lang, "obligatorisk_pension.mail1.htmlbody")
                    ).render(context)
                    for lang in ("kl", "da")
                ]
            )
            + "</body></html>",
        )
        send_mail(
            recipient=recipient,
            subject=subject,
            textbody="\n\n----\n\n".join(textbody),
            htmlbody="\n".join(htmlbody),
        )

    def send_mail_to_office(self, recipient, object):
        subject = gettext_lang("da", "obligatorisk_pension.mail2.subject")
        engine = Engine.get_default()
        context = Context({"object": object})
        textbody = "\n\n----\n\n".join(
            [
                engine.from_string(
                    gettext_lang(lang, "obligatorisk_pension.mail2.textbody")
                ).render(context)
                for lang in ("kl", "da")
            ]
        )
        htmlbody = (
            "<html><body>"
            + "<hr/>".join(
                [
                    engine.from_string(
                        gettext_lang(lang, "obligatorisk_pension.mail2.htmlbody")
                    ).render(context)
                    for lang in ("kl", "da")
                ]
            )
            + "</body></html>"
        )

        attachments = [("data.txt", textbody, magic.from_buffer(textbody, mime=True))]

        for fileobject in object.filer.all():
            name = fileobject.fil.name
            data = fileobject.fil.read()
            mimetype = magic.from_buffer(data, mime=True)
            attachments.append((name, data, mimetype))

        send_mail(
            recipient=recipient,
            subject=subject,
            textbody=textbody,
            htmlbody=htmlbody,
            attachments=attachments,
        )
