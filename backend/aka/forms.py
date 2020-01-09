import csv
import logging
from io import StringIO

import chardet
from aka.data.fordringsgruppe import groups
from aka.utils import get_ordereddict_key_index, spreadsheet_col_letter
from django import forms
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.forms import ValidationError
from django.utils.datetime_safe import date
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

valid_date_formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d', '%Y-%m-%d', '%d-%m-%y']


class CsvUploadMixin(object):

    def clean_file(self):
        file = self.cleaned_data['file']
        if file.size > settings.MAX_UPLOAD_FILESIZE:
            raise ValidationError('file_too_large', code='error.upload_too_large', params={'maxsize': settings.MAX_UPLOAD_FILESIZE})

        file.seek(0)
        data = file.read()
        charset = chardet.detect(data)
        if charset is None or charset['encoding'] is None:
            # Raise errors that affect the whole file,
            # preventing the contents from being validated
            raise ValidationError('error.upload_no_encoding', code='error.upload_no_encoding')
        subforms = []
        try:
            csv_reader = csv.DictReader(StringIO(data.decode(charset['encoding'])))
            rows = [row for row in csv_reader]  # Catch csv reading errors early
        except csv.Error as e:
            raise ValidationError('error.upload_read_error', code='error.upload_read_error')
        if len(rows) == 0:
            raise ValidationError('error.upload_empty', code='error.upload_empty')

        # Use self.add_error to add validation errors on the file contents,
        # as there may be several in the same file
        for row_index, row in enumerate(rows, start=1):
            subform = self.subform_class(data=self.transform_row(row))
            if not subform.is_valid():  # Catch row errors early
                for field, errorlist in subform.errors.items():
                    if 'error.required' in errorlist and field not in row:
                        self.add_error('file', ValidationError(
                            'error.upload_validation_header',
                            code='error.upload_validation_header',
                            params={'field': field}
                        ))
                    try:
                        col_index = get_ordereddict_key_index(row, field)
                    except ValueError:
                        col_index = None
                    for error in errorlist.as_data():
                        self.add_error('file', ValidationError(
                            'error.upload_validation_item',
                            code='error.upload_validation_item',
                            params={
                                'field': field,
                                'message': (str(error.message), error.params),
                                'row': row_index,
                                'col': col_index,
                                'col_letter': spreadsheet_col_letter(col_index)
                            }
                        ))
            subforms.append(subform)
        self.subforms = subforms
        return file

    # To be overridden in subclasses
    def transform_row(self, row):
        return row


class KontoForm(forms.Form):

    from_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=True,
        error_messages={'required': 'error.required', 'invalid': 'error.invalid_date'},
        input_formats=valid_date_formats
    )
    to_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=True,
        error_messages={'required': 'error.required', 'invalid': 'error.invalid_date'},
        input_formats=valid_date_formats
    )

    def clean(self):
        if 'from_date' in self.cleaned_data and 'to_date' in self.cleaned_data:
            if self.cleaned_data['from_date'] > self.cleaned_data['to_date']:
                raise ValidationError(_('error.from_date_before_to_date'), code='error.from_date_before_to_date')


class InkassoForm(forms.Form):

    fordringshaver = forms.CharField(
        required=True,
        error_messages={'required': 'error.required', 'invalid': 'error.invalid_date'},
    )
    debitor = forms.CharField(
        required=True,
        error_messages={'required': 'error.required', 'invalid': 'error.invalid_date'},
    )
    fordringshaver2 = forms.CharField(
        required=False
    )
    fordringsgruppe = forms.ChoiceField(
        required=True,
        choices=[(item['id'], item['name']) for item in groups],
        error_messages={'invalid_choice': 'error.fordringsgruppe_not_found', 'required': 'error.required'}
    )
    fordringstype = forms.ChoiceField(
        required=True,
        choices=[],
        error_messages={'invalid_choice': 'error.fordringstype_not_found', 'required': 'error.required'}
    )
    periodestart = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=True,
        error_messages={'required': 'error.required', 'invalid': 'error.invalid_date'},
        input_formats=valid_date_formats
    )
    periodeslut = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=True,
        error_messages={'required': 'error.required', 'invalid': 'error.invalid_date'},
        input_formats=valid_date_formats
    )
    barns_cpr = forms.CharField(
        required=False
    )
    ekstern_sagsnummer = forms.CharField(
        required=True,
        error_messages={'required': 'error.required'},
    )
    hovedstol = forms.DecimalField(
        decimal_places=2,
        required=True,
        error_messages={'required': 'error.required'}
    )
    hovedstol_posteringstekst = forms.CharField(
        required=True,
        error_messages={'required': 'error.required'},
    )
    kontaktperson = forms.CharField(
        required=False,
    )
    forfaldsdato = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=True,
        error_messages={'required': 'error.required', 'invalid': 'error.invalid_date'},
        input_formats=valid_date_formats
    )
    betalingsdato = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=True,
        error_messages={'required': 'error.required', 'invalid': 'error.invalid_date'},
        input_formats=valid_date_formats
    )
    foraeldelsesdato = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=True,
        error_messages={'required': 'error.required', 'invalid': 'error.invalid_date'},
        input_formats=valid_date_formats
    )
    noter = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 50}),
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
                    for x in groups
                    if int(x['id']) == int(group_id)
                ][0]
                # Set type choices based on this subgroup
                self.fields['fordringstype'].choices = [
                    ("%d.%d" % (item['group_id'], item['type_id']), item['type_id'])
                    for item in subgroup
                ]
                # type = [x for x in subgroup if x['type_id']]

        except IndexError:
            pass

    def clean_fordringsgruppe(self):
        value = self.cleaned_data['fordringsgruppe']
        items = [
            item for item in groups
            if int(item['id']) == int(value)
        ]
        if len(items) > 1:
            raise ValidationError('error.multiple_fordringsgruppe_found')
        return value

    def clean(self):
        cleaned_data = super(InkassoForm, self).clean()
        start = cleaned_data.get('periodestart')
        end = cleaned_data.get('periodeslut')
        if start and end and start > end:
            self.add_error('periodeslut', ValidationError('error.start_date_before_end_date'))

        # Whether barns_cpr is required depends on the group and type selected
        group_id = cleaned_data.get('fordringsgruppe')
        type_id = cleaned_data.get('fordringstype')
        if group_id is not None and type_id is not None:
            subgroups = [x['sub_groups'] for x in groups if int(x['id']) == int(group_id)][0]
            type = [x for x in subgroups if "%d.%d" % (x['group_id'], x['type_id']) == type_id][0]
            if type.get('has_child_cpr') and not cleaned_data.get('barns_cpr'):
                self.add_error('barns_cpr', ValidationError(self.fields['barns_cpr'].error_messages['required'], code='required'))
        print(self.errors)

    @staticmethod
    def convert_group_type_text(groupname, typename):
        group_match = [group for group in groups if group['name'] == groupname]
        if not group_match:
            raise ValidationError('error.fordringsgruppe_not_found')
        group = group_match[0]
        type_match = [type for type in group['sub_groups'] if type['name'] == typename]
        if not type_match:
            raise ValidationError('error.fordringstype_not_found')
        type = type_match[0]
        return (group['id'], "%d.%d" % (type['group_id'], type['type_id']))


class InkassoCoDebitorFormItem(forms.Form):

    cpr = forms.CharField(
        required=False,
        min_length=10,
        max_length=10
    )
    cvr = forms.CharField(
        required=False,
        min_length=8,
        max_length=8
    )


class InkassoUploadForm(CsvUploadMixin, forms.Form):

    subform_class = InkassoForm

    file = forms.FileField(
        required=True,
        validators=[
            FileExtensionValidator(['csv'], code='error.invalid_extension')
        ]
    )

    def transform_row(self, row):
        (row['fordringsgruppe'], row['fordringstype']) = InkassoForm.convert_group_type_text(row['fordringsgruppe'], row['fordringstype'])
        return row


class InterestNoteForm(forms.Form):

    year = forms.ChoiceField(
        choices=[(x, x) for x in range(date.today().year - 10, date.today().year + 1)],
        required=True,
        error_messages={'required': 'error.required'},
        widget=forms.Select(attrs={'class': 'dropdown'}),
        initial=date.today().year
    )
    month = forms.ChoiceField(
        choices=[(x, x) for x in range(1, 13)],
        required=True,
        error_messages={'required': 'error.required'},
        widget=forms.Select(attrs={'class': 'dropdown'}),
        initial=date.today().month
    )


class LoentraekForm(forms.Form):

    year = forms.ChoiceField(
        choices=[(x, x) for x in range(date.today().year - 10, date.today().year + 1)],
        required=True,
        error_messages={'required': 'error.required'},
        widget=forms.Select(attrs={'class': 'dropdown'}),
        initial=date.today().year
    )
    month = forms.ChoiceField(
        choices=[(x, x) for x in range(1, 13)],
        required=True,
        error_messages={'required': 'error.required'},
        widget=forms.Select(attrs={'class': 'dropdown'}),
        initial=date.today().month
    )
    total_amount = forms.DecimalField(
        decimal_places=2,
        required=True,
        error_messages={'required': 'error.required'},
        min_value=0.01,
    )

    def check_sum(self, formset, add_error=True):
        formset_sum = sum([subform.cleaned_data['amount']
                           for subform in formset
                           if subform.cleaned_data])
        total = self.cleaned_data['total_amount']
        if formset_sum != total:
            if add_error:
                self.add_error('total_amount', ValidationError('loentraek.sum_mismatch', code='loentraek.sum_mismatch'))
            return False
        return True


class LoentraekFormItem(forms.Form):

    cpr = forms.CharField(
        required=True,
        error_messages={'required': 'error.required'},
        min_length=10,
        max_length=10
    )
    agreement_number = forms.CharField(
        required=True,
        error_messages={'required': 'error.required'}
    )
    amount = forms.DecimalField(
        decimal_places=2,
        required=True,
        error_messages={'required': 'error.required'},
        min_value=0.01
    )
    net_salary = forms.DecimalField(
        decimal_places=2,
        required=False,
        error_messages={'required': 'error.required'},
        min_value=0.01
    )


class LoentraekUploadForm(CsvUploadMixin, LoentraekForm):

    file = forms.FileField(
        required=True,
        validators=[
            FileExtensionValidator(['csv'], code='error.invalid_extension')
        ]
    )

    subform_class = LoentraekFormItem


class NedskrivningForm(forms.Form):

    debitor = forms.CharField(
        required=True,
        error_messages={'required': 'error.required'}
    )
    ekstern_sagsnummer = forms.CharField(
        required=True,
        max_length=10,
        error_messages={'required': 'error.required'}
    )
    beloeb = forms.DecimalField(
        decimal_places=2,
        required=True,
        error_messages={'required': 'error.required'}
    )
    sekvensnummer = forms.CharField(
        max_length=30,
        error_messages={'required': 'error.required'}
    )


class NedskrivningUploadForm(CsvUploadMixin, forms.Form):

    file = forms.FileField(
        required=True,
        validators=[
            FileExtensionValidator(['csv'])
        ],
    )

    subform_class = NedskrivningForm
