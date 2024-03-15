from datetime import date

from aka.widgets import TranslatedSelect
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, widgets
from dynamic_forms import DynamicField, DynamicFormMixin
from obligatorisk_pension.models import (
    ObligatoriskPension,
    ObligatoriskPensionFile,
    ObligatoriskPensionSelskab,
)

from aka.forms import FileField


class SkatteårForm(DynamicFormMixin, forms.Form):
    skatteår = DynamicField(
        forms.ChoiceField,
        required=True,
        error_messages={"required": "error.required"},
        choices=lambda form: (
            (x, str(x)) for x in range(date.today().year - 5, date.today().year + 1)
        ),
        initial=lambda form: date.today().year,
    )


class ObligatoriskPensionSelskabForm(forms.ModelForm):
    class Meta:
        model = ObligatoriskPensionSelskab
        fields = (
            "id",
            "grønlandsk",
            "land",
            "pensionsselskab",
        )

    grønlandsk = forms.BooleanField(
        initial=True,
        widget=TranslatedSelect(
            choices=(
                (True, "common.ja"),
                (False, "common.nej"),
            ),
        ),
        required=False,
        error_messages={"required": "error.required"},
    )
    land = forms.CharField(
        required=False,
    )
    pensionsselskab = forms.CharField(
        required=True,
        error_messages={"required": "error.required"},
    )


ObligatoriskPensionSelskabFormSet = inlineformset_factory(
    parent_model=ObligatoriskPension,
    model=ObligatoriskPensionSelskab,
    form=ObligatoriskPensionSelskabForm,
    min_num=1,
    extra=0,
    can_delete=True,
    validate_min=True,
)


class ObligatoriskPensionFilForm(forms.ModelForm):
    class Meta:
        model = ObligatoriskPensionFile
        fields = (
            "fil",
            "beskrivelse",
        )

    fil = FileField(
        error_messages={"required": "error.required"},
    )


ObligatoriskPensionFilFormSet = inlineformset_factory(
    parent_model=ObligatoriskPension,
    model=ObligatoriskPensionFile,
    form=ObligatoriskPensionFilForm,
    min_num=1,
    extra=0,
    can_delete=True,
    validate_min=True,
)


class ObligatoriskPensionForm(forms.ModelForm):
    class Meta:
        model = ObligatoriskPension
        fields = [
            "navn",
            "adresse",
            "kommune",
            "email",
            "beløb",
        ]

    def __init__(self, *args, **kwargs):
        initial = kwargs.pop("initial", None)
        self.selskabformset = ObligatoriskPensionSelskabFormSet(*args, **kwargs)
        self.filformset = ObligatoriskPensionFilFormSet(*args, **kwargs)
        super().__init__(*args, initial=initial, **kwargs)

    def is_valid(self):
        return (
            super().is_valid()
            and self.selskabformset.is_valid()
            and self.filformset.is_valid()
        )

    def save(self, commit=True, **kwargs):
        instance = super().save(commit=False)
        for key, value in kwargs.items():
            setattr(instance, key, value)
        self.selskabformset.instance = instance
        self.filformset.instance = instance
        if self.selskabformset.is_valid() and self.filformset.is_valid():
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
        widget=TranslatedSelect(attrs={"class": "dropdown"}),
    )
    email = forms.EmailField(
        required=True,
        error_messages={"required": "error.required"},
    )
    beløb = forms.DecimalField(
        decimal_places=2,
        required=True,
        error_messages={"required": "error.required"},
        min_value=0.01,
        localize=True,
    )

    def clean_land(self):
        if not self.cleaned_data.get("grønlandsk") and not self.cleaned_data.get(
            "land"
        ):
            raise ValidationError(
                self.fields["land"].error_messages["required"], code="error.required"
            )
        return self.cleaned_data.get("land")
