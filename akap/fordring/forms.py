import logging
from datetime import date

from aka.data.fordringsgruppe import groups, groups_by_id, subgroups_by_id
from aka.forms import CsvUploadMixin, FileField, PrependCharField
from django import forms
from django.core.validators import (
    FileExtensionValidator,
    MaxLengthValidator,
    MinLengthValidator,
    RegexValidator,
)
from django.forms import TextInput, ValidationError
from django.forms.formsets import formset_factory

logger = logging.getLogger(__name__)

valid_date_formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d", "%d-%m-%y"]


cprvalidator = RegexValidator(r"^\d{10}$", "error.invalid_cpr")
cvrvalidator = RegexValidator(r"^\d{8}$", "error.invalid_cvr")
cprcvrvalidator = RegexValidator(r"^\d{8}(\d{2})?$", "error.invalid_cpr_cvr")
csepcprcvrvalidator = RegexValidator(
    r"^\d{8}(\d{2})?(,\d{8}(\d{2})?)*$", "error.invalid_cpr_cvr"
)


class InkassoForm(forms.Form):
    debitor = forms.CharField(
        required=True,
        error_messages={"required": "error.required"},
    )
    fordringshaver2 = forms.CharField(required=False)

    dokumentation = FileField(required=False)

    fordringsgruppe = forms.ChoiceField(
        required=True,
        choices=[(item["id"], item["name"]) for item in groups],
        error_messages={
            "invalid_choice": "error.fordringsgruppe_not_found",
            "required": "error.required",
        },
    )
    fordringstype = forms.ChoiceField(
        required=True,
        choices=[],
        error_messages={
            "invalid_choice": "error.fordringstype_not_found",
            "required": "error.required",
        },
    )
    periodestart = forms.DateField(
        widget=forms.DateInput(attrs={"class": "datepicker"}),
        required=False,
        error_messages={"required": "error.required", "invalid": "error.invalid_date"},
        input_formats=valid_date_formats,
    )
    periodeslut = forms.DateField(
        widget=forms.DateInput(attrs={"class": "datepicker"}),
        required=False,
        error_messages={"required": "error.required", "invalid": "error.invalid_date"},
        input_formats=valid_date_formats,
    )
    barns_cpr = PrependCharField(
        required=False,
        widget=TextInput(attrs={"data-cpr": "true"}),
        validators=[cprvalidator],
        prepend_char="0",
        total_length=10,
    )
    ekstern_sagsnummer = forms.CharField(
        required=True,
        error_messages={"required": "error.required"},
    )
    hovedstol = forms.DecimalField(
        decimal_places=2,
        required=True,
        error_messages={"required": "error.required"},
        localize=True,
    )
    hovedstol_posteringstekst = forms.CharField(
        required=True,
        error_messages={"required": "error.required"},
    )
    kontaktperson = forms.CharField(
        required=False,
    )
    forfaldsdato = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "datepicker",
                "data-validate-after": "#id_betalingsdato",
                "data-validate-after-errormessage": "fordring.bill_date_before_due_date",
            }
        ),
        required=True,
        error_messages={"required": "error.required", "invalid": "error.invalid_date"},
        input_formats=valid_date_formats,
    )
    betalingsdato = forms.DateField(
        widget=forms.DateInput(attrs={"class": "datepicker"}),
        required=True,
        error_messages={"required": "error.required", "invalid": "error.invalid_date"},
        input_formats=valid_date_formats,
    )
    foraeldelsesdato = forms.DateField(
        widget=forms.DateInput(attrs={"class": "datepicker"}),
        required=True,
        error_messages={"required": "error.required", "invalid": "error.invalid_date"},
        input_formats=valid_date_formats,
    )
    noter = forms.CharField(widget=forms.Textarea(attrs={"cols": 50}), required=False)

    def __init__(self, *args, **kwargs):
        super(InkassoForm, self).__init__(*args, **kwargs)
        self.set_typefield_choices()

        for validator in self.fields["barns_cpr"].validators:
            if isinstance(validator, (MinLengthValidator, MaxLengthValidator)):
                validator.message = "error.invalid_cpr"

    def set_typefield_choices(self):
        try:
            # Get selected group id
            group_id = self.fields["fordringsgruppe"].widget.value_from_datadict(
                self.data, self.files, self.add_prefix("fordringsgruppe")
            )
            if group_id is not None:
                # Find out which subgroup exists for this id
                subgroup = [
                    x["sub_groups"] for x in groups if int(x["id"]) == int(group_id)
                ][0]
                # Set type choices based on this subgroup
                self.fields["fordringstype"].choices = [
                    ("%d.%d" % (item["group_id"], item["type_id"]), item["type_id"])
                    for item in subgroup
                ]
                # type = [x for x in subgroup if x['type_id']]

        except IndexError:
            pass

    def clean_fordringsgruppe(self):
        value = self.cleaned_data["fordringsgruppe"]
        items = [item for item in groups if int(item["id"]) == int(value)]
        if len(items) > 1:
            raise ValidationError("error.multiple_fordringsgruppe_found")
        return value

    # Prisme depends on the value for periodestart, so set it to today if
    # it was not specified.
    def clean_periodestart(self):
        value = self.cleaned_data.get("periodestart")

        if not value:
            value = date.today()

        return value

    # Prisme depends on the value for periodeslut, so set it to today if
    # it was not specified.
    def clean_periodeslut(self):
        value = self.cleaned_data.get("periodeslut")
        if not value:
            value = date.today()
        return value

    def clean(self):
        cleaned_data = super(InkassoForm, self).clean()
        start = cleaned_data.get("periodestart")
        end = cleaned_data.get("periodeslut")
        if start and end and start > end:
            self.add_error(
                "periodeslut", ValidationError("error.start_date_before_end_date")
            )

        # Whether barns_cpr is required depends on the group and type selected
        group_id = cleaned_data.get("fordringsgruppe")
        type_id = cleaned_data.get("fordringstype")
        if group_id is not None and type_id is not None:
            subgroups = [
                x["sub_groups"] for x in groups if int(x["id"]) == int(group_id)
            ][0]
            type = [
                x
                for x in subgroups
                if "%d.%d" % (x["group_id"], x["type_id"]) == type_id
            ][0]
            if type.get("has_child_cpr") and not cleaned_data.get("barns_cpr"):
                self.add_error(
                    "barns_cpr",
                    ValidationError(
                        self.fields["barns_cpr"].error_messages["required"],
                        code="required",
                    ),
                )

    @staticmethod
    def convert_group_type_text(groupname, typename):
        for group in groups:
            for type in group["sub_groups"]:
                if str(type["group_id"]) == str(groupname) and str(
                    type["type_id"]
                ) == str(typename):
                    return (group["id"], "%d.%d" % (type["group_id"], type["type_id"]))

        group_match = [group for group in groups if group["name"] == groupname]
        if not group_match:
            raise ValidationError("error.fordringsgruppe_not_found")
        group = group_match[0]
        type_match = [type for type in group["sub_groups"] if type["name"] == typename]
        if not type_match:
            raise ValidationError("error.fordringstype_not_found")
        type = type_match[0]
        return (group["id"], "%d.%d" % (type["group_id"], type["type_id"]))

    @staticmethod
    def get_group_type_text(group_type_str):
        group_id, type_id = group_type_str.split(".")
        return subgroups_by_id[int(group_id)][int(type_id)]["name"]

    @staticmethod
    def get_group_name(group_id):
        return groups_by_id[int(group_id)]["name"]


class InkassoCoDebitorFormItem(forms.Form):
    cpr = PrependCharField(
        required=False, min_length=10, max_length=10, prepend_char="0", total_length=10
    )
    cvr = PrependCharField(
        required=False, min_length=8, max_length=8, prepend_char="0", total_length=8
    )


InkassoCoDebitorFormSet = formset_factory(form=InkassoCoDebitorFormItem)


class InkassoUploadFormRow(InkassoForm):
    fordringshaver = forms.CharField(
        required=False,
    )
    meddebitorer = forms.CharField(required=False, validators=[csepcprcvrvalidator])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(1, 100):
            self.fields["codebtor_%d" % i] = forms.CharField(
                required=False, validators=[cprcvrvalidator]
            )


class InkassoUploadForm(CsvUploadMixin, forms.Form):
    subform_class = InkassoUploadFormRow

    field_order = [
        "fordringshaver",
        "debitor",
        "fordringshaver2",
        "fordringsgruppe",
        "fordringstype",
        "barns_cpr",
        "ekstern_sagsnummer",
        "hovedstol",
        "hovedstol_posteringstekst",
        "bankrente",  # Disse felter anvendes svjv. ikke
        "bankrente_posteringstekst",
        "bankgebyr",
        "bankgebyr_posteringstekst",
        "rente",
        "rente_posteringstekst",
        "kontaktperson",
        "periodestart",
        "periodeslut",
        "forfaldsdato",
        "betalingsdato",
        "foraeldelsesdato",
        "noter",
        "meddebitorer",
    ]

    file = FileField(
        required=True,
        validators=[
            FileExtensionValidator(["csv", "txt"], code="error.invalid_extension")
        ],
    )

    def transform_row(self, row):
        (
            row["fordringsgruppe"],
            row["fordringstype"],
        ) = InkassoForm.convert_group_type_text(
            row["fordringsgruppe"], row["fordringstype"]
        )
        return row
