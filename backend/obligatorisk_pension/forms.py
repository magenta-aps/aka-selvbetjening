from django.conf import settings
from django import forms
from django.forms import widgets
from django.utils.translation import gettext_lazy as _


class ObligatoriskPensionForm(forms.Form):
    navn = forms.CharField(
        label=_("Navn"),
        required=True,
        error_messages={"required": "error.required"},
    )
    adresse = forms.CharField(
        label=_("Adresse"),
        required=True,
        error_messages={"required": "error.required"},
        widget=widgets.Textarea,
    )
    kommune = forms.ChoiceField(
        choices=((m["code"], m["name"]) for m in settings.MUNICIPALITIES),
        required=True,
        error_messages={"required": "error.required"},
    )
    email = forms.EmailField(
        label=_("Email-adresse"),
        required=True,
        error_messages={"required": "error.required"},
    )
    grønlandsk = forms.ChoiceField(
        label=_("Grønlandsk pensionsordning"),
        choices=((True, _("Ja")), (False, _("Nej")),),
        widget=widgets.RadioSelect,
        required=True,
        error_messages={"required": "error.required"},
    )
    land = forms.CharField(
        label=_("Land"),
        required=False,
    )
    pensionsselskab = forms.CharField(
        label=_("Pensionsselskab"),
        required=True,
        error_messages={"required": "error.required"},
    )
