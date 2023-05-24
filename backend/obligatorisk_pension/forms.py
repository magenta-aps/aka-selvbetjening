import re
from django.conf import settings
from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils.translation import gettext_lazy as _

from obligatorisk_pension.models import ObligatoriskPension
from obligatorisk_pension.models import ObligatoriskPensionFile


class FileSetMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for i in range(0, 10):
            self.fields[f"file_data_{i}"] = forms.FileField(
                allow_empty_file=True,
                required=False,
            )
            self.fields[f"file_description_{i}"] = forms.CharField(
                max_length=1000,
                widget=widgets.TextInput(
                    attrs={
                        "placeholder": _("obligatorisk_pension.filbeskrivelse"),
                        "data-trans": "obligatorisk_pension.filbeskrivelse",
                        "data-trans-attr": "placeholder",
                    }
                ),
                required=False,
            )

    def get_filled_files(self):
        # Returns a list of tuples (file, description)
        if self.is_bound:
            r = re.compile(r"form-\d+-file_data_(\d+)")
            files = []
            for name, file in self.files.items():
                m = r.match(name)
                if m:
                    description = self.cleaned_data.get(
                        f"file_description_{m.group(1)}", ""
                    )
                    files.append(
                        (
                            file,
                            description,
                        )
                    )
            return files
        return None

    def get_nonfile_data(self):
        if self.is_bound:
            return {
                k: v for k, v in self.cleaned_data.items() if not k.startswith("file_")
            }

    @property
    def filefields(self):
        return (field for field in self if field.name.startswith("file_"))

    def _save_m2m(self):
        super()._save_m2m()
        for file, description in self.get_filled_files():
            ObligatoriskPensionFile.objects.create(
                fil=file,
                beskrivelse=description,
                obligatoriskpension=self.instance,
            )


class ObligatoriskPensionForm(FileSetMixin, forms.ModelForm):
    class Meta:
        model = ObligatoriskPension
        fields = [
            "navn",
            "adresse",
            "kommune",
            "email",
            "grønlandsk",
            "land",
            "pensionsselskab",
        ]

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
    grønlandsk = forms.BooleanField(
        widget=widgets.RadioSelect(
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

    def clean_land(self):
        if not self.cleaned_data.get("grønlandsk") and not self.cleaned_data.get("land"):
            raise ValidationError(self.fields["land"].error_messages['required'], code='error.required')
        return self.cleaned_data.get("land")
