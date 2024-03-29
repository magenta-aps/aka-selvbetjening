from aka.forms import AcceptingMultipleChoiceField, RadioSelect, valid_date_formats
from django import forms
from django.core.exceptions import ValidationError
from django.forms import MultipleHiddenInput
from django.utils.translation import gettext_lazy as _
from dynamic_forms import DynamicField, DynamicFormMixin


class KontoForm(DynamicFormMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        self.cprcvr_choices = kwargs.pop("cprcvr_choices", ())
        super(KontoForm, self).__init__(*args, **kwargs)

    from_date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "datepicker"}),
        required=False,
        error_messages={"required": "error.required", "invalid": "error.invalid_date"},
        input_formats=valid_date_formats,
    )
    to_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "datepicker",
                "data-validate-after": "#id_from_date",
                "data-validate-after-errormessage": "error.from_date_before_to_date",
            }
        ),
        required=False,
        error_messages={"required": "error.required", "invalid": "error.invalid_date"},
        input_formats=valid_date_formats,
    )
    open_closed = forms.IntegerField(
        widget=RadioSelect(
            choices=[
                (0, "konto.entries_open"),
                (1, "konto.entries_closed"),
                (2, "konto.entries_all"),
            ],
        ),
        error_messages={"required": "error.required"},
        initial=2,
    )
    hidden = AcceptingMultipleChoiceField(widget=MultipleHiddenInput, required=False)
    cprcvr = DynamicField(
        forms.ChoiceField, required=False, choices=lambda form: form.cprcvr_choices
    )

    def clean(self):
        if (
            self.cleaned_data.get("from_date") is not None
            and self.cleaned_data.get("to_date") is not None
        ):
            if self.cleaned_data["from_date"] > self.cleaned_data["to_date"]:
                raise ValidationError(
                    _("error.from_date_before_to_date"),
                    code="error.from_date_before_to_date",
                )
