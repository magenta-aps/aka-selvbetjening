import logging
from aka.widgets import TranslatedSelect
from django import forms
from django.forms import ValidationError
from django.utils.datetime_safe import date
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

logger = logging.getLogger(__name__)

valid_date_formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d", "%d-%m-%y"]
cprvalidator = RegexValidator(r"^\d{10}$", "error.invalid_cpr")
cvrvalidator = RegexValidator(r"^\d{8}$", "error.invalid_cvr")
cprcvrvalidator = RegexValidator(r"^\d{8}(\d{2})?$", "error.invalid_cpr_cvr")


class UdbytteForm(forms.Form):
    navn = forms.CharField(
        label=_("Navn på udfylder"),
        required=True,
        error_messages={"required": "error.required"},
    )
    revisionsfirma = forms.CharField(
        label=_("Revisionsfirma"),
        required=True,
        error_messages={"required": "error.required"},
    )
    virksomhedsnavn = forms.CharField(
        label=_("Virksomhedsnavn"),
        error_messages={"required": "error.required"},
    )
    cvr = forms.CharField(
        label=_("CVR"),
        validators=[cvrvalidator],
        required=True,
        error_messages={"required": "error.required", "invalid": "error.invalid_cvr"},
    )
    email = forms.EmailField(
        label=_("Email-adresse"),
        required=True,
        error_messages={"required": "error.required", "invalid": "error.invalid_email"},
    )
    regnskabsår = forms.ChoiceField(
        label=_("Udbyttet vedrører regnskabsåret"),
        required=True,
        choices=lambda: (
            (year, str(year))
            for year in range(date.today().year, date.today().year - 6, -1)
        ),
    )
    u1_udfyldt = forms.BooleanField(
        label=_("Har du allerede udfyldt U1?"),
        required=False,
        widget=TranslatedSelect(
            choices=((None, "---------"), ("0", "No"), ("1", "Yes"))
        ),
    )
    udbytte = forms.DecimalField(
        label=_("Udbetalt/godskrevet udbytte i DKK, før skat"),
        required=True,
        localize=True,
        error_messages={
            "required": "error.required",
            "invalid": "error.number_required",
        },
    )

    noter = forms.CharField(
        label=_("Særlige oplysninger"),
        widget=forms.Textarea(),
        required=False,
    )
    by = forms.CharField(
        label=_("By"),
        required=True,
        error_messages={"required": "error.required"},
    )
    dato = forms.DateField(
        label=_("Dato"),
        widget=forms.DateInput(attrs={"class": "datepicker"}),
        required=True,
        error_messages={"required": "error.required", "invalid": "error.invalid_date"},
        input_formats=valid_date_formats,
    )
    underskriftsberettiget = forms.CharField(
        label=_("Navn på underskriftsberettiget for selskabet"),
        required=True,
        error_messages={"required": "error.required"},
    )

    def clean_with_formset(self, formset):
        formset_sum = sum([item.cleaned_data.get("udbytte", 0) for item in formset])
        form_udbytte = self.cleaned_data["udbytte"]
        if form_udbytte != formset_sum:
            self.add_error("udbytte", ValidationError("error.udbytte_sum_mismatch"))


class UdbytteFormItem(forms.Form):
    cpr_cvr_tin = forms.CharField(
        label=_("CPR-nr / CVR-nr / TIN"),
        validators=[cprcvrvalidator],
        required=True,
        error_messages={
            "required": "error.required",
            "invalid": "error.invalid_cpr_cvr",
        },
    )
    navn = forms.CharField(
        label=_("Navn"),
        required=True,
        error_messages={"required": "error.required"},
    )
    adresse = forms.CharField(
        label=_("Adresse"),
        required=True,
        error_messages={"required": "error.required"},
    )
    postnummer = forms.CharField(
        label=_("Postnummer"),
        required=True,
        error_messages={"required": "error.required"},
    )
    by = forms.CharField(
        label=_("By"),
        required=True,
        error_messages={"required": "error.required"},
    )
    land = forms.CharField(
        label=_("Land"),
        required=True,
        error_messages={"required": "error.required"},
    )
    udbytte = forms.DecimalField(
        label=_("Udbetalt/godskrevet udbytte i DKK, før skat"),
        required=True,
        localize=True,
        error_messages={
            "required": "error.required",
            "invalid": "error.number_required",
        },
    )
