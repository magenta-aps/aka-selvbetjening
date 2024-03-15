import logging

from aka.forms import CsvUploadMixin, PrependCharField
from aka.widgets import TranslatedSelect
from django import forms
from django.core.validators import (
    FileExtensionValidator,
    MaxLengthValidator,
    MinLengthValidator,
    RegexValidator,
)
from django.forms import TextInput, ValidationError
from django.utils.datetime_safe import date
from dynamic_forms import DynamicField, DynamicFormMixin

from aka.forms import FileField

logger = logging.getLogger(__name__)


cprvalidator = RegexValidator(r"^\d{10}$", "error.invalid_cpr")
cvrvalidator = RegexValidator(r"^\d{8}$", "error.invalid_cvr")


class LoentraekForm(DynamicFormMixin, forms.Form):
    year = DynamicField(
        forms.ChoiceField,
        choices=lambda form: [
            (x, str(x)) for x in range(date.today().year - 10, date.today().year + 1)
        ],
        required=True,
        error_messages={"required": "error.required"},
        widget=forms.Select(attrs={"class": "dropdown"}),
        initial=date.today().year,
    )
    month = DynamicField(
        forms.ChoiceField,
        choices=[
            (1, "January"),
            (2, "February"),
            (3, "March"),
            (4, "April"),
            (5, "May"),
            (6, "June"),
            (7, "July"),
            (8, "August"),
            (9, "September"),
            (10, "October"),
            (11, "November"),
            (12, "December"),
        ],
        required=True,
        error_messages={"required": "error.required"},
        widget=TranslatedSelect(attrs={"class": "dropdown"}),
        initial=lambda form: date.today().month,
    )
    total_amount = forms.DecimalField(
        decimal_places=2,
        required=True,
        error_messages={"required": "error.required"},
        min_value=0.01,
        localize=True,
    )

    def check_sum(self, formset, add_error=True):
        formset_sum = sum(
            [
                subform.cleaned_data["amount"]
                for subform in formset
                if subform.cleaned_data
            ]
        )
        total = self.cleaned_data["total_amount"]
        if formset_sum != total:
            if add_error:
                self.add_error(
                    "total_amount",
                    ValidationError(
                        "loentraek.sum_mismatch", code="loentraek.sum_mismatch"
                    ),
                )
            return False
        return True


class LoentraekFormItem(forms.Form):
    cpr = PrependCharField(
        required=True,
        error_messages={"required": "error.required"},
        widget=TextInput(attrs={"data-cpr": "true"}),
        validators=[cprvalidator],
        prepend_char="0",
        total_length=10,
    )
    agreement_number = PrependCharField(
        required=True,
        error_messages={"required": "error.required"},
        prepend_char="0",
        total_length=8,
    )
    amount = forms.DecimalField(
        decimal_places=2,
        required=True,
        error_messages={"required": "error.required"},
        min_value=0.01,
        localize=True,
    )
    net_salary = forms.DecimalField(
        decimal_places=2,
        required=False,
        error_messages={"required": "error.required"},
        min_value=0.01,
        localize=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for validator in self.fields["cpr"].validators:
            if isinstance(validator, (MinLengthValidator, MaxLengthValidator)):
                validator.message = "error.invalid_cpr"


class LoentraekUploadForm(CsvUploadMixin, LoentraekForm):
    file = FileField(
        required=True,
        validators=[
            FileExtensionValidator(["csv", "txt"], code="error.invalid_extension")
        ],
    )

    subform_class = LoentraekFormItem

    field_order = [
        "cpr",
        "agreement_number",
        "amount",
        "net_salary",
        "head_reference_number",
        "item_reference_number",
    ]
