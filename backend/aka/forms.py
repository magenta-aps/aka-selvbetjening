import chardet
import csv
import logging
import re
from aka.utils import get_ordereddict_key_index
from aka.utils import spreadsheet_col_letter
from django import forms
from django.conf import settings
from django.core.validators import RegexValidator
from django.forms import ValidationError
from io import StringIO

logger = logging.getLogger(__name__)

valid_date_formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d", "%d-%m-%y"]


cprvalidator = RegexValidator(r"^\d{10}$", "error.invalid_cpr")
cvrvalidator = RegexValidator(r"^\d{8}$", "error.invalid_cvr")
cprcvrvalidator = RegexValidator(r"^\d{8}(\d{2})?$", "error.invalid_cpr_cvr")
csepcprcvrvalidator = RegexValidator(
    r"^\d{8}(\d{2})?(,\d{8}(\d{2})?)*$", "error.invalid_cpr_cvr"
)


class CsvUploadMixin(object):
    akadialect = csv.register_dialect("aka", "excel", delimiter=";")

    field_order = None

    def clean_file(self):
        file = self.cleaned_data["file"]
        if file.size > settings.MAX_UPLOAD_FILESIZE:
            raise ValidationError(
                "file_too_large",
                code="error.upload_too_large",
                params={"maxsize": settings.MAX_UPLOAD_FILESIZE},
            )

        file.seek(0)
        data = file.read()
        charset = chardet.detect(data)
        if charset is None or charset["encoding"] is None:
            # Raise errors that affect the whole file,
            # preventing the contents from being validated
            raise ValidationError(
                "error.upload_no_encoding", code="error.upload_no_encoding"
            )
        subforms = []
        try:
            data = data.decode(charset["encoding"])
            data = re.sub('("[\n\r]+|$)', "\n", data, flags=re.MULTILINE)
            data = re.sub('(^|[\n\r]+)"', "\n", data, flags=re.MULTILINE)
            csv_reader = csv.DictReader(
                StringIO(data), dialect="aka", fieldnames=self.field_order
            )
            rows = [row for row in csv_reader]  # Catch csv reading errors early
        except csv.Error:
            raise ValidationError(
                "error.upload_read_error", code="error.upload_read_error"
            )
        if len(rows) == 0:
            raise ValidationError("error.upload_empty", code="error.upload_empty")

        # Use self.add_error to add validation errors on the file contents,
        # as there may be several in the same file
        for row_index, row in enumerate(rows, start=2):
            data = self.transform_row(row)
            subform = self.subform_class(data=data)
            missing = subform.fields.keys() - data
            if missing:
                missing_required = False
                for field in missing:
                    if subform.fields[field].required:
                        self.add_error(
                            "file",
                            ValidationError(
                                "error.upload_validation_header",
                                code="error.upload_validation_header",
                                params={"field": field},
                            ),
                        )
                        missing_required = True
                if missing_required:
                    break
            if not subform.is_valid():  # Catch row errors early
                for field, errorlist in subform.errors.items():
                    if (
                        "error.required" in errorlist
                        and field not in row
                        and field not in missing
                    ):
                        self.add_error(
                            "file",
                            ValidationError(
                                "error.upload_validation_header",
                                code="error.upload_validation_header",
                                params={"field": field},
                            ),
                        )
                    try:
                        col_index = get_ordereddict_key_index(row, field)
                    except ValueError:
                        col_index = None
                    for error in errorlist.as_data():
                        self.add_error(
                            "file",
                            ValidationError(
                                "error.upload_validation_item",
                                code="error.upload_validation_item",
                                params={
                                    "field": field,
                                    "message": (str(error.message), error.params),
                                    "row": row_index,
                                    "col": col_index,
                                    "col_letter": spreadsheet_col_letter(col_index),
                                },
                            ),
                        )
            subforms.append(subform)
        self.subforms = subforms
        return file

    # To be overridden in subclasses
    def transform_row(self, row):
        return row


class RadioSelect(forms.RadioSelect):
    option_template_name = "aka/util/optionfield.html"


class AcceptingMultipleChoiceField(forms.MultipleChoiceField):
    def valid_value(self, value):
        return True


class PrependCharField(forms.CharField):
    def __init__(self, *args, prepend_char, total_length, **kwargs):
        super().__init__(*args, **kwargs)
        self.prepend_char = prepend_char
        self.total_length = total_length

    def to_python(self, value):
        value = super().to_python(value)
        if value == self.empty_value:
            return value
        if len(self.prepend_char) > 0:
            while len(value) < self.total_length:
                value = self.prepend_char + value
        return value
