import logging

from django import forms
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.forms import ValidationError

from .utils import getSharedJson

logger = logging.getLogger(__name__)
fordringJson = getSharedJson('fordringsgruppe.json')


class InkassoForm(forms.Form):

    fordringshaver = forms.CharField(
        required=True,
        error_messages={'required': 'required_field'}
    )
    debitor = forms.CharField(
        required=True,
        error_messages={'required': 'required_field'}
    )
    fordringshaver2 = forms.CharField(
        required=False
    )
    fordringsgruppe = forms.ChoiceField(
        required=True,
        choices=[(item['id'], item['value']) for item in fordringJson],
        error_messages={'invalid_choice': 'fordringsgruppe_not_found', 'required': 'required_field'}
    )
    fordringstype = forms.ChoiceField(
        required=True,
        choices=[],
        error_messages={'invalid_choice': 'fordringstype_not_found', 'required': 'required_field'}
    )
    periodestart = forms.DateField(
        required=True,
        error_messages={'required': 'required_field'}
    )
    periodeslut = forms.DateField(
        required=True,
        error_messages={'required': 'required_field'}
    )
    barns_cpr = forms.CharField(
        required=False
    )
    ekstern_sagsnummer = forms.CharField(
        required=False
    )
    hovedstol = forms.DecimalField(
        decimal_places=2,
        required=True,
        error_messages={'required': 'required_field'}
    )
    hovedstol_posteringstekst = forms.CharField(
        required=False
    )
    kontaktperson = forms.CharField(
        required=False,
        # error_messages={'required': 'required_field'}
    )
    forfaldsdato = forms.DateField(
        required=True,
        error_messages={'required': 'required_field'}
    )
    betalingsdato = forms.DateField(
        required=True,
        error_messages={'required': 'required_field'}
    )
    foraeldelsesdato = forms.DateField(
        required=True,
        error_messages={'required': 'required_field'}
    )
    noter = forms.CharField(
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(InkassoForm, self).__init__(*args, **kwargs)
        self.set_typefield_choices()

    def set_typefield_choices(self):
        try:
            # Get selected group id
            group_id = self.fields['fordringsgruppe'].widget.value_from_datadict(
                self.data,
                self.files,
                self.add_prefix('fordringsgruppe')
            )
            if group_id is not None:
                # Find out which subgroup exists for this id
                subgroup = [
                    x['sub_groups']
                    for x in fordringJson
                    if int(x['id']) == int(group_id)
                ][0]
                # Set type choices based on this subgroup
                self.fields['fordringstype'].choices = [
                    (item['id'], item['value'])
                    for item in subgroup
                ]
        except IndexError:
            pass

    def clean_fordringsgruppe(self):
        value = self.cleaned_data['fordringsgruppe']
        items = [
            item for item in fordringJson
            if int(item['id']) == int(value)
        ]
        if len(items) > 1:
            raise ValidationError('multiple_fordringsgruppe_found')
        return value

    def clean(self):
        cleaned_data = super(InkassoForm, self).clean()
        start = cleaned_data.get('periodestart')
        end = cleaned_data.get('periodeslut')
        if start and end and start > end:
            self.add_error('periodeslut', ValidationError('start_date_before_end_date'))


class InkassoUploadForm(forms.Form):

    file = forms.FileField(
        required=True,
        validators=[
            FileExtensionValidator(['csv'])
        ]
    )

    def clean_file(self):
        file = self.cleaned_data['file']
        if file.size > settings.MAX_UPLOAD_FILESIZE:
            raise ValidationError('file_too_large')
        return file


class LoentraekForm(forms.Form):

    cvrnummer = forms.IntegerField(max_value=99999999)
    traekmaaned = forms.IntegerField(min_value=1, max_value=12)
    traekaar = forms.IntegerField(min_value=1900, max_value=2200)


class NedskrivningForm(forms.Form):

    fordringshaver = forms.CharField(
        required=True,
        error_messages={'required': 'required_field'}
    )
    debitor = forms.CharField(
        required=True,
        error_messages={'required': 'required_field'}
    )
    ekstern_sagsnummer = forms.CharField(
        required=True,
        max_length=10,
    )
    beloeb = forms.DecimalField(
        decimal_places=2,
        required=True,
        error_messages={'required': 'required_field'}
    )
    sekvensnummer = forms.CharField(
        max_length=30
    )


class NedskrivningUploadForm(forms.Form):

    file = forms.FileField(
        required=True,
        validators=[
            FileExtensionValidator(['csv'])
        ]
    )

    def clean_file(self):
        file = self.cleaned_data['file']
        if file.size > settings.MAX_UPLOAD_FILESIZE:
            raise ValidationError('file_too_large')
        return file
