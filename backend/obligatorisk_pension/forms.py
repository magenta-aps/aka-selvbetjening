import re
from datetime import date
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import widgets, inlineformset_factory
from django.utils.translation import gettext_lazy as _
from obligatorisk_pension.models import ObligatoriskPension
from obligatorisk_pension.models import ObligatoriskPensionFile
from obligatorisk_pension.models import ObligatoriskPensionSelskab


class SkatteårForm(forms.Form):
    def __init__(self, *args, **kwargs):
        current_year = date.today().year
        kwargs["initial"]["skatteår"] = current_year
        super().__init__(*args, **kwargs)
        self.fields["skatteår"].choices = (
            (x, str(x)) for x in range(current_year - 5, current_year + 1)
        )
        self.initial["skatteår"] = current_year

    skatteår = forms.ChoiceField(
        required=True,
        error_messages={"required": "error.required"},
    )


class ObligatoriskPensionSelskabForm(forms.ModelForm):
    class Meta:
        model = ObligatoriskPensionSelskab
        fields = (
            "id",
            "grønlandsk",
            "land",
            "pensionsselskab",
            "beløb",
        )

    grønlandsk = forms.BooleanField(
        initial=True,
        widget=widgets.Select(
            choices=(
                (True, _("Ja")),
                (False, _("Nej")),
            ),
        ),
        required=True,
        error_messages={"required": "error.required"},
    )
    land = forms.CharField(
        required=False,
    )
    pensionsselskab = forms.CharField(
        required=True,
        error_messages={"required": "error.required"},
    )
    beløb = forms.DecimalField(
        decimal_places=2,
        required=True,
        error_messages={"required": "error.required", "invalid": "error.number_required"},
        localize=True,
        min_value=0.00,
    )


ObligatoriskPensionSelskabFormSet = inlineformset_factory(
    parent_model=ObligatoriskPension,
    model=ObligatoriskPensionSelskab,
    form=ObligatoriskPensionSelskabForm,
    extra=1,
    can_delete=True,
)


class ObligatoriskPensionFilForm(forms.ModelForm):
    class Meta:
        model = ObligatoriskPensionFile
        fields = ("fil","beskrivelse",)


ObligatoriskPensionFilFormSet = inlineformset_factory(
    parent_model=ObligatoriskPension,
    model=ObligatoriskPensionFile,
    form=ObligatoriskPensionFilForm,
    extra=1,
    can_delete=True,
)


class ObligatoriskPensionForm(forms.ModelForm):
    class Meta:
        model = ObligatoriskPension
        fields = [
            "navn",
            "adresse",
            "kommune",
            "email",
        ]

    def __init__(self, *args, **kwargs):
        self.selskabformset = ObligatoriskPensionSelskabFormSet(*args, **kwargs)
        self.filformset = ObligatoriskPensionFilFormSet(*args, **kwargs)
        super().__init__(*args, **kwargs)

    def is_valid(self):
        return super().is_valid() and self.selskabformset.is_valid() and self.filformset.is_valid()

    def save(self, commit=True, **kwargs):
        instance = super().save(commit=False)
        if self.selskabformset.is_valid() and self.filformset.is_valid():
            if commit:
                instance.save()
            self.selskabformset.save(commit)
            self.filformset.save(commit)
        return instance

    navn = forms.CharField(
        required=True,
        error_messages={"required": "error.required"},
    )
    adresse = forms.CharField(
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
        required=True,
        error_messages={"required": "error.required"},
    )

    def clean_land(self):
        if not self.cleaned_data.get("grønlandsk") and not self.cleaned_data.get(
            "land"
        ):
            raise ValidationError(
                self.fields["land"].error_messages["required"], code="error.required"
            )
        return self.cleaned_data.get("land")
