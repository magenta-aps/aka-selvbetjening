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

        if self.instance:
            self.existing_files = []
            for i, file in enumerate(self.instance.filer.all()):
                id_key = key = f"file_existing_id_{i}"
                self.fields[key] = forms.ChoiceField(
                    widget=widgets.HiddenInput(),
                    disabled=True,
                    choices=((file.pk, file.pk),),
                )
                self.existing_files.append(self[key])
                self.initial[key] = file.pk

                key = f"file_existing_delete_{i}"
                self.fields[key] = forms.BooleanField(
                    widget=widgets.CheckboxInput(attrs={"title": _("Behold fil")}),
                    label=file.fil.name,
                    required=False,
                )
                self.initial[key] = True
                self[id_key].keep_field = self[key]

                key = f"file_existing_description_{i}"
                self.fields[key] = forms.CharField(
                    max_length=255,
                    widget=widgets.TextInput(attrs={"placeholder": _("Beskrivelse")}),
                    required=False,
                )
                self.initial[key] = file.beskrivelse
                self[id_key].description_field = self[key]

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

    def get_existing_files(self):
        if self.is_bound:
            data = {}
            for id_field in self.existing_files:
                data[id_field.value()] = {
                    "keep": id_field.keep_field.value(),
                    "description": id_field.description_field.value(),
                }
            return data

    def _save_m2m(self):
        super()._save_m2m()
        for file, description in self.get_filled_files():
            ObligatoriskPensionFile.objects.create(
                fil=file,
                beskrivelse=description,
                obligatoriskpension=self.instance,
            )
        for pk, data in self.get_existing_files().items():
            file_object_qs = ObligatoriskPensionFile.objects.filter(pk=pk)
            if data["keep"] is False:
                file_object_qs.delete()
            else:
                file_object_qs.update(beskrivelse=data["description"])


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
        fields = [
            "id",
            "grønlandsk",
            "land",
            "pensionsselskab",
            "beløb",
        ]

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
)


class ObligatoriskPensionForm(FileSetMixin, forms.ModelForm):
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
        super().__init__(*args, **kwargs)

    def is_valid(self):
        return super().is_valid() and self.selskabformset.is_valid()

    def save(self, commit=True):
        instance = super().save(commit=False)
        self.selskabformset.instance = instance
        if self.selskabformset.is_valid():
            instance.save()
            self.selskabformset.save()
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
