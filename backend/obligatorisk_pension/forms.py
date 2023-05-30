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
        )

    grønlandsk = forms.BooleanField(
        initial=True,
        widget=widgets.Select(
            choices=(
                (True, _("Ja")),
                (False, _("Nej")),
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

    fil = forms.FileField(
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
        ]

    def __init__(self, *args, **kwargs):
        self.selskabformset = ObligatoriskPensionSelskabFormSet(*args, **kwargs)
        self.filformset = ObligatoriskPensionFilFormSet(*args, **kwargs)
        super().__init__(*args, **kwargs)

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
