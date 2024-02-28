import logging

from aka.widgets import TranslatedSelect
from django import forms
from django.utils.datetime_safe import date
from dynamic_forms import DynamicField, DynamicFormMixin

logger = logging.getLogger(__name__)


class InterestNoteForm(DynamicFormMixin, forms.Form):
    year = DynamicField(
        forms.ChoiceField,
        choices=lambda form: [
            (x, str(x)) for x in range(date.today().year - 10, date.today().year + 1)
        ],
        required=True,
        error_messages={"required": "error.required"},
        widget=forms.Select(attrs={"class": "dropdown"}),
        initial=lambda form: date.today().year,
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
