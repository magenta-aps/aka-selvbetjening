import logging
from aka.forms import CsvUploadMixin
from django import forms
from django.core.validators import FileExtensionValidator

logger = logging.getLogger(__name__)


class NedskrivningForm(forms.Form):
    fordringshaver = forms.CharField(
        required=False,
    )

    debitor = forms.CharField(
        required=True, error_messages={"required": "error.required"}
    )
    ekstern_sagsnummer = forms.CharField(
        required=True, error_messages={"required": "error.required"}
    )
    beloeb = forms.DecimalField(
        decimal_places=2,
        required=True,
        error_messages={"required": "error.required"},
        localize=True,
    )
    sekvensnummer = forms.CharField(
        max_length=30, error_messages={"required": "error.required"}
    )


class NedskrivningUploadForm(CsvUploadMixin, forms.Form):
    file = forms.FileField(
        required=True,
        validators=[
            FileExtensionValidator(["csv", "txt"], code="error.invalid_extension")
        ],
    )

    subform_class = NedskrivningForm
    field_order = [
        "fordringshaver",  # Not sent to Prisme service
        "debitor",
        "inkassonummer",  # Not sent to Prisme service
        "beloeb",
        "oprindeligt_overfoert_beloeb",  # Not sent to Prisme service
        "ekstern_sagsnummer",
        "sekvensnummer",
    ]
