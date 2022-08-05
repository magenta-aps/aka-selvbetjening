import json
import logging
import re
import uuid
from io import BytesIO
from typing import List

from aka.clients.prisme import Prisme, PrismeException
from aka.clients.prisme import PrismeAKIRequest
from aka.clients.prisme import PrismeAKITotalRequest
from aka.clients.prisme import PrismeClaimRequest
from aka.clients.prisme import PrismeImpairmentRequest
from aka.clients.prisme import PrismeInterestNoteRequest
from aka.clients.prisme import PrismePayrollRequest
from aka.clients.prisme import PrismePayrollRequestLine
from aka.clients.prisme import PrismeSELRequest
from aka.clients.prisme import PrismeSELTotalRequest
from aka.data.fordringsgruppe import groups
from aka.forms import InkassoCoDebitorFormItem
from aka.forms import InkassoForm, InkassoUploadForm
from aka.forms import InterestNoteForm
from aka.forms import KontoForm
from aka.forms import LoentraekForm
from aka.forms import LoentraekFormItem
from aka.forms import LoentraekUploadForm
from aka.forms import NedskrivningForm
from aka.forms import NedskrivningUploadForm
from aka.mixins import AkaMixin
from aka.mixins import ErrorHandlerMixin
from aka.mixins import HasUserMixin
from aka.mixins import IsContentMixin
from aka.mixins import JsonRendererMixin
from aka.mixins import PdfRendererMixin
from aka.mixins import RequireCvrMixin
from aka.mixins import SimpleGetFormMixin
from aka.mixins import SpreadsheetRendererMixin
from aka.utils import Field, Cell, Row, Table
from aka.utils import chunks
from aka.utils import flatten
from aka.utils import get_ordereddict_key_index
from aka.utils import render_pdf
from aka.utils import spreadsheet_col_letter
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import formset_factory
from django.http import Http404
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import redirect
from django.template import Engine, Context
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils import translation
from django.utils.datetime_safe import date
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _, gettext
from django.utils.translation.trans_real import DjangoTranslation
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.views.i18n import JavaScriptCatalog
from extra_views import FormSetView


class CustomJavaScriptCatalog(JavaScriptCatalog):

    js_catalog_template = r"""
    {% autoescape off %}
    (function(globals) {
    var django = globals.django || (globals.django = {});
    django.catalog = django.catalog || {};
    {% if catalog_str %}
    django.catalog["{{ locale }}"] = {{ catalog_str }};
    {% endif %}
    }(this));
    {% endautoescape %}
    """

    def get(self, request, locale, *args, **kwargs):
        domain = kwargs.get('domain', self.domain)
        self.locale = locale
        # If packages are not provided, default to all installed packages, as
        # DjangoTranslation without localedirs harvests them all.
        packages = kwargs.get('packages', '')
        packages = packages.split('+') if packages else self.packages
        paths = self.get_paths(packages) if packages else None
        self.translation = DjangoTranslation(locale, domain=domain, localedirs=paths)
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = {'locale': self.locale}
        context.update(super(CustomJavaScriptCatalog, self).get_context_data(**kwargs))
        context['catalog_str'] = \
            json.dumps(context['catalog'], sort_keys=True, indent=2) \
            if context['catalog'] else None
        context['formats_str'] = json.dumps(context['formats'], sort_keys=True, indent=2)
        return context

    def render_to_response(self, context, **response_kwargs):
        template = Engine().from_string(self.js_catalog_template)
        return HttpResponse(template.render(Context(context)), 'text/javascript; charset="utf-8"')


class SetLanguageView(View):

    def post(self, request, *args, **kwargs):
        language = request.POST.get('language', settings.LANGUAGE_CODE)
        translation.activate(language)
        # request.session[translation.LANGUAGE_SESSION_KEY] = language
        response = JsonResponse("OK", safe=False)
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            settings.LOCALE_MAP.get(language, language),
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            path=settings.LANGUAGE_COOKIE_PATH,
        )
        return response


class GetPDFView(RequireCvrMixin, View):
    def get(self, request, *args, **kwargs):
        pdf_id = kwargs['pdf_id']
        try:
            pdf_context = request.session['receipts'][pdf_id]
        except KeyError:
            raise Http404
        return FileResponse(
            BytesIO(render_pdf(pdf_context['template'], pdf_context['context'])),
            filename=pdf_context['filename'],
            as_attachment=True
        )


class GetReceiptView(GetPDFView):
    type = 'receipts'


logger = logging.getLogger(__name__)


class IndexTemplateView(HasUserMixin, AkaMixin, TemplateView):
    template_name = 'index.html'

    @method_decorator(ensure_csrf_cookie)
    def get(self, *args, **kwargs):
        return super(IndexTemplateView, self).get(*args, **kwargs)


class ChooseCvrView(AkaMixin, TemplateView):

    template_name = "choose_cvr.html"

    def get_context_data(self, **kwargs):
        context = {
            'cvrs': self.request.session.get('cvrs'),
            'back': self.request.GET.get('back')
        }
        context.update(kwargs)
        return super().get_context_data(**context)

    def get(self, request, *args, **kwargs):
        cvr = request.GET.get("cvr")
        if cvr and cvr in self.request.session.get('cvrs'):
            back = self.request.GET.get('back')
            request.session['user_info']['CVR'] = cvr
            request.session['has_checked_cvr'] = True
            request.session.save()
            return redirect(back)
        return super().get(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class KontoView(HasUserMixin, SimpleGetFormMixin, PdfRendererMixin, JsonRendererMixin, SpreadsheetRendererMixin, IsContentMixin, TemplateView):

    form_class = KontoForm
    template_name = 'aka/account/account.html'
    pdf_template_name = 'aka/account/account_pdf.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sections = None
        self._data = {}
        self._total = {}
        self._prisme = None

    def form_valid(self, form):
        self.form = form
        try:
            self.load_sections(form)
        except PrismeException as e:
            form.add_error(None, e.as_validationerror)
            return self.form_invalid(form)
        if 'format' in self.request.GET:
            response = self.render()
            if response is not None:
                return response
        return super(KontoView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['cprcvr_choices'] = [
            (getattr(self, key), "%s: %s" % (key.upper(), getattr(self, key)))
            for key in ('cpr', 'cvr')
            if getattr(self, key)
        ]
        return kwargs

    def get_context_data(self, **kwargs):
        context = {}
        if self.form.is_bound:
            formdata = self.form.cleaned_data
            context.update({
                'sections': self.sections,
                'date': date.today().strftime('%d/%m/%Y'),
                'period': {
                    'from_date': formdata['from_date'].strftime('%d-%m-%Y') if formdata.get('from_date') is not None else None,
                    'to_date': formdata['to_date'].strftime('%d-%m-%Y') if formdata.get('to_date') is not None else None
                },
                'cprcvr': self.cprcvr_choice
            })
            if self.is_pdf:
                context['pages'] = self.get_pages()

        context.update(kwargs)
        return super().get_context_data(**context)

    def get_filename(self):
        try:
            from_date = self.form.cleaned_data['from_date'].strftime('%Y-%m-%d')
        except (KeyError, ValueError, AttributeError):
            from_date = ""
        try:
            to_date = self.form.cleaned_data['to_date'].strftime('%Y-%m-%d')
        except (KeyError, ValueError, AttributeError):
            to_date = ""
        return _("account.filename").format(
            from_date=from_date,
            to_date=to_date
        )

    def get_sheetname(self):
        return "Kontoudtog"

    def hide_fields(self, form, fields):
        return [
            field for field in fields
            if field.name not in form.cleaned_data['hidden']
        ]

    @property
    def prisme(self):
        if not self._prisme:
            self._prisme = Prisme()
        return self._prisme

    def get_lookup_class(self, key):
        if key == 'sel':
            return PrismeSELRequest
        if key == 'aki':
            return PrismeAKIRequest

    def get_total_lookup_class(self, key):
        if key == 'sel':
            return PrismeSELTotalRequest
        if key == 'aki':
            return PrismeAKITotalRequest

    @property
    def cprcvr_choice(self):
        cprcvr = str(self.form.cleaned_data.get('cprcvr') or self.cpr or self.cvr)
        if cprcvr == str(self.cpr):
            return (cprcvr, 'cpr')
        elif cprcvr == str(self.cvr):
            return (cprcvr, 'cvr')
        else:
            logger.info("cprcvr_choice got: "+str({'cprcvr': cprcvr, 'cpr': self.cpr, 'cvr': self.cvr}))

    def get_rows_by_key(self, key) -> List[Row]:
        if key not in self._data:
            try:
                (cprcvr, c) = self.cprcvr_choice
                lookup_class = self.get_lookup_class(key)
                prisme_reply = self.prisme.process_service(lookup_class(
                    cprcvr,
                    self.form.cleaned_data['from_date'],
                    self.form.cleaned_data['to_date'],
                    self.form.cleaned_data['open_closed']
                ), "account", self.cpr, self.cvr)
                self._data[key] = []
                if len(prisme_reply) == 0:
                    return []
                for entry in prisme_reply[0]:
                    row = Row()
                    for field in self.get_fields_by_key(key):
                        value = getattr(entry, field.name)
                        if field.modifier:
                            value = field.modifier(value)
                        row.cells.append(Cell(field=field, value=value,))
                    self._data[key].append(row)
            except PrismeException:
                pass
        return self._data.get(key, [])

    def get_total_data(self, key) -> dict:
        if key not in self._total:
            try:
                (cprcvr, c) = self.cprcvr_choice
                lookup_class = self.get_total_lookup_class(key)
                prisme_reply = self.prisme.process_service(lookup_class(
                    cprcvr
                ), "account", self.cpr, self.cvr)
                if len(prisme_reply) == 0:
                    return None
                reply = prisme_reply[0]
                self._total[key] = {
                    key: getattr(reply, key)
                    for key in ['total_claim', 'total_payment', 'total_sum', 'total_restance']
                }
            except PrismeException:
                pass
        return self._total.get(key)

    def load_sections(self, form):
        self.sections = []
        key = self.request.GET.get("key")
        keys = [key] if key else ['sel', 'aki']
        for key in keys:
            rows = self.get_rows_by_key(key)
            total = self.get_total_data(key)
            self.sections.append({
                'key': key,
                'title': 'account.title_' + key,
                'fields': self.hide_fields(form, self.get_fields_by_key(key)),
                'rows': rows,
                'total': total
            })

    def get_pages(self, key=None):
        if key is None:
            key = self.request.GET.get("key")
        if key:
            pages = []
            max_columns_per_page = 8  # if there are more columns than this number, we do a split
            line_field = Field(name='index', klass='nb', transkey='account.linje', title='Linje')
            for section in self.sections:
                total = section['total']
                if len(section['rows']):
                    # item_collection is a dict of all items for a key (key = 'aki' or 'sel')
                    # it contains title, fields, total, and a list of rows
                    # Read fields in chunks, creating a new page for each chunk
                    for page_fields, startcol in chunks(section['fields'], max_columns_per_page):
                        pages.append(Table(
                            name=section['key'],
                            fields=[line_field] + page_fields,
                            rows=[
                                Row(cells=[Cell(field=line_field, value=rownumber)] + row.cells[startcol:startcol+max_columns_per_page])
                                for rownumber, row in enumerate(section['rows'], 1)
                            ],
                            total=total
                        ))

                        # Only show totals in first page of the section
                        total = None
                else:
                    pages.append(Table(
                        name=section['key'],
                        fields=[line_field] + section['fields']
                    ))
            return pages
        return []

    def get_rows(self) -> List[Row]:
        return self.get_rows_by_key(self.key)

    def get_extra(self) -> dict:
        total = self.get_total_data(self.key)
        if total:
            return {
                gettext("account.%s" % x): total[x]
                for x in ['total_claim', 'total_payment', 'total_sum', 'total_restance']
            }

    def get_fields(self) -> List[Field]:
        return self.get_fields_by_key(self.key)

    def get_fields_by_key(self, key='sel') -> List[Field]:
        fields = [
            Field(name='account_number', klass='nb'),
            Field(name='transaction_date', klass='nb'),
            Field(name='accounting_date', klass='nb'),
            Field(name='debitor_group_id', klass='nb'),
            Field(name='debitor_group_name', klass='nb'),
            Field(name='voucher', klass='nb'),
            Field(name='text', klass=''),
            Field(name='payment_code', klass='nb'),
            Field(name='payment_code_name', klass='nb'),
            Field(name='amount', klass='nb numbercell', number=True),
            Field(name='remaining_amount', klass='nb numbercell', number=True),
            Field(name='due_date', klass='nb'),
            Field(name='closed_date', klass='nb'),
            Field(name='last_settlement_voucher', klass='nb'),
            Field(name='collection_letter_date', klass='nb'),
            Field(name='collection_letter_code', klass='nb'),
            Field(name='claim_type_code', klass='nb'),
            Field(name='invoice_number', klass='nb'),
            Field(name='transaction_type', klass='nb'),
        ]
        if key == 'sel':
            fields += [
                Field(name='rate_number', klass='nb'),
                Field(name='claim_type_code',
                    labelkey='submitted_to_claims',
                    klass='nb',
                    modifier=lambda d: (d == 'INDR'),
                    boolean=True
                )
            ]
        if key == 'aki':
            fields += [
                Field(name='child_claimant', klass='nb')
            ]
        for field in fields:
            field.transkey = "account.%s" % (field.labelkey or field.name)
            field.title = _(field.transkey).replace("&shy;", "")
        return fields


class InkassoSagView(RequireCvrMixin, ErrorHandlerMixin, IsContentMixin, FormSetView, FormView):

    form_class = InkassoForm
    template_name = 'aka/claim/form.html'

    def get_formset(self):
        return formset_factory(InkassoCoDebitorFormItem, **self.get_factory_kwargs())

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        formset = self.construct_formset()
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        return self.form_invalid(form, formset)

    @staticmethod
    def send_claim(claimant_id, form, codebtors, cpr, cvr):
        prisme = Prisme()
        if prisme.mock:
            return ['1234']

        claim_type = form.cleaned_data['fordringstype'].split(".")

        claim = PrismeClaimRequest(
            claimant_id=claimant_id,
            cpr_cvr=form.cleaned_data.get('debitor'),
            external_claimant=form.cleaned_data.get('fordringshaver2'),
            claim_group_number=claim_type[0],
            claim_type=claim_type[1],
            child_cpr=form.cleaned_data.get('barns_cpr'),
            claim_ref=form.cleaned_data.get('ekstern_sagsnummer'),
            amount_balance=form.cleaned_data.get('hovedstol'),
            text=form.cleaned_data.get('hovedstol_posteringstekst'),
            created_by=form.cleaned_data.get('kontaktperson'),
            period_start=form.cleaned_data.get('periodestart'),
            period_end=form.cleaned_data.get('periodeslut'),
            due_date=form.cleaned_data.get('forfaldsdato'),
            founded_date=form.cleaned_data.get('betalingsdato'),
            obsolete_date=form.cleaned_data.get('foraeldelsesdato'),
            notes=form.cleaned_data.get('noter'),
            codebtors=codebtors,
            files=[file for name, file in form.files.items()]
        )
        prisme_replies = prisme.process_service(claim, 'fordring', cpr, cvr)
        return [reply.rec_id for reply in prisme_replies]

    def form_valid(self, form, formset):
        if len(self.claimant_ids) == 0:
            form.add_error(None, _("login.error_no_claimants"))
            return self.form_invalid(form, formset)
        codebtors = []
        if formset:
            for subform in formset:
                cpr = subform.cleaned_data.get("cpr")
                cvr = subform.cleaned_data.get("cvr")
                if cpr is not None:
                    codebtors.append(cpr)
                elif cvr is not None:
                    codebtors.append(cvr)
        pdf_id = None
        try:
            rec_ids = InkassoSagView.send_claim(self.claimant_ids[0], form, codebtors, self.cpr, self.cvr)
            if rec_ids:
                pdf_id = InkassoSagView.store_pdf_context(
                    self.request.session,
                    self.cvr,
                    [{**form.cleaned_data, 'rec_ids': rec_ids}],
                )
        except PrismeException as e:
            form.add_error(None, e.as_validationerror)
            return self.form_invalid(form, formset)

        return TemplateResponse(
            request=self.request,
            template="aka/claim/success.html",
            context={
                'rec_ids': rec_ids,
                'upload': False,
                'pdf_id': pdf_id,
            },
            using=self.template_engine
        )

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    @staticmethod
    def store_pdf_context(session, cvr, data):
        now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        pdf_context = {
            'received_date': date.today(),
            'cvr': cvr,
            'lines': [
                {
                    'debitor': subdata.get('debitor'),
                    'fordringsgruppe': InkassoForm.get_group_name(subdata.get('fordringsgruppe')),
                    'fordringstype': InkassoForm.get_group_type_text(subdata.get('fordringstype')),
                    'ekstern_sagsnummer': subdata.get('ekstern_sagsnummer'),
                    'hovedstol': subdata.get('hovedstol'),
                    'forfaldsdato': subdata.get('forfaldsdato'),
                    'rec_ids': subdata['rec_ids'],
                }
                for subdata in data
            ]
        }
        if 'receipts' not in session:
            session['receipts'] = {}
        pdf_id = str(uuid.uuid4())
        session['receipts'][pdf_id] = {
            'context': pdf_context,
            'filename': f'kvittering_fordring_{now}.pdf',
            'template': 'aka/claim/receipt.html',
        }
        session.modified = True
        return pdf_id


class InkassoSagUploadView(RequireCvrMixin, ErrorHandlerMixin, IsContentMixin, FormView):
    form_class = InkassoUploadForm
    template_name = 'aka/claim/upload.html'
    parallel = False

    def handle_subform(self, subform):
        codebtor_re = re.compile(r"^codebtor_\d+$")
        claimant = subform.cleaned_data['fordringshaver'] or self.claimant_ids[0]
        codebtors = []
        for field, value in subform.cleaned_data.items():
            match = codebtor_re.match(field)
            if match and len(value):
                codebtors.append(value)
            if field == 'meddebitorer' and len(value):
                codebtors += value.split(',')
        try:
            rec_ids = InkassoSagView.send_claim(claimant, subform, codebtors, self.cpr, self.cvr)
            return {**subform.cleaned_data, 'rec_ids': rec_ids}
        except PrismeException as e:
            logger.exception(e)
            return {'error': e}

    def form_valid(self, form):
        if len(self.claimant_ids) == 0:
            form.add_error(None, ValidationError(_("login.error_no_claimants"), 'login.error_no_claimants'))
            return self.form_invalid(form)

        if self.parallel:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                results = list(executor.map(self.handle_subform, [subform for subform in form.subforms]))
        else:
            results = [self.handle_subform(subform) for subform in form.subforms]

        responses = []
        errors = []
        for result in results:
            if 'rec_ids' in result:
                responses.append(result)
            if 'error' in result:
                errors.append(result['error'].as_error_dict)

        pdf_id = None
        if responses:
            pdf_id = InkassoSagView.store_pdf_context(self.request.session, self.cvr, responses)

        return TemplateResponse(
            request=self.request,
            template="aka/claim/success.html",
            context={
                'rec_ids': flatten([response['rec_ids'] for response in responses]),
                'upload': True,
                'errors': errors,
                'pdf_id': pdf_id
            },
            using=self.template_engine
        )


class FordringReceiptView(GetReceiptView):
    context = 'fordring'


class InkassoGroupDataView(View):
    def get(self, request, var='', *args, **kwargs):
        data = json.dumps(groups)
        if var:
            return HttpResponse("%s = %s" % (var, data), content_type='text/javascript')
        return HttpResponse(data, content_type='application/json')


# 6.2

class LoentraekView(RequireCvrMixin, IsContentMixin, FormSetView, FormView):

    form_class = LoentraekForm
    template_name = 'aka/payroll/form.html'

    def get_formset(self):
        return formset_factory(LoentraekFormItem, **self.get_factory_kwargs())

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        formset = self.construct_formset()
        if form.is_valid() and formset.is_valid() and form.check_sum(formset, True):
            return self.form_valid(form, formset)
        return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        prisme = Prisme()
        try:
            if prisme.mock:
                rec_ids = ['1234']
            else:
                payroll = PrismePayrollRequest(
                    cvr=self.cvr,
                    date=date(int(form.cleaned_data['year']), int(form.cleaned_data['month']), 1),
                    received_date=date.today(),
                    amount=form.cleaned_data['total_amount'],
                    lines=[
                        PrismePayrollRequestLine(
                            subform.cleaned_data.get('cpr'),
                            subform.cleaned_data.get('agreement_number'),
                            subform.cleaned_data.get('amount'),
                            subform.cleaned_data.get('net_salary')
                        )
                        for subform in formset
                        if subform.cleaned_data
                    ]
                )
                rec_ids = [x.rec_id for x in prisme.process_service(payroll, 'loentraek', self.cpr, self.cvr)]
            if rec_ids:
                pdf_id = self.store_pdf_context(form.cleaned_data, [subform.cleaned_data for subform in formset], rec_ids)
            return TemplateResponse(
                request=self.request,
                template="aka/payroll/success.html",
                context={
                    'rec_ids': rec_ids,
                    'pdf_id': pdf_id,
                },
                using=self.template_engine
            )
        except PrismeException as e:
            found = False
            if e.code == 250 or e.code == '250':
                d = e.as_error_dict
                if 'params' in d and 'nr' in d['params']:
                    for subform in formset:
                        if subform.cleaned_data.get('agreement_number') == d['params']['nr']:
                            subform.add_error('agreement_number', e.as_validationerror)
                            found = True
            else:
                logger.info("Got error code %s from prisme" % str(e.code))
            if not found:
                form.add_error(None, e.as_validationerror)
            return self.form_invalid(form, formset)

    def form_invalid(self, form, formset):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

    def store_pdf_context(self, formdata, formsetdata, rec_ids):
        now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        pdf_context = {
            'received_date': date.today(),
            'date': {'year': int(formdata['year']), 'month': int(formdata['month'])},
            'total_amount': formdata['total_amount'],
            'rec_ids': rec_ids,
            'cvr': self.cvr,
            'lines': [
                {
                    'cpr': subformdata.get('cpr'),
                    'agreement_number': subformdata.get('agreement_number'),
                    'amount': subformdata.get('amount'),
                    'net_salary': subformdata.get('net_salary')
                }
                for subformdata in formsetdata
            ]
        }
        session = self.request.session
        if 'receipts' not in session:
            session['receipts'] = {}
        pdf_id = str(uuid.uuid4())
        session['receipts'][pdf_id] = {
            'context': pdf_context,
            'filename': f'kvittering_løntræk_{now}.pdf',
            'template': 'aka/payroll/receipt.html',
        }
        session.modified = True
        return pdf_id


class LoentraekReceiptView(GetReceiptView):
    context = 'loentraek'


class LoentraekUploadView(LoentraekView):
    form_class = LoentraekUploadForm
    template_name = 'aka/payroll/upload.html'

    def forms_valid(self, forms):
        for subform in forms:
            if not subform.is_valid():
                return False
        return True

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            if self.forms_valid(form.subforms) and form.check_sum(form.subforms, True):
                return self.form_valid(form, form.subforms)
        return self.form_invalid(form, form.subforms if hasattr(form, "subforms") else None)

    def form_invalid(self, form, formset=None):
        if formset is not None:
            for row_index, subform in enumerate(formset, start=2):
                if subform.errors:
                    for field, errorlist in subform.errors.items():
                        try:
                            col_index = get_ordereddict_key_index(subform.fields, field)
                        except ValueError:
                            col_index = None
                        for error in errorlist.as_data():
                            form.add_error('file', ValidationError(
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
        return self.render_to_response(
            self.get_context_data(form=form)
        )


# 6.4

class NedskrivningView(RequireCvrMixin, ErrorHandlerMixin, IsContentMixin, FormView):

    form_class = NedskrivningForm
    template_name = 'aka/impairment/form.html'

    def send_impairment(self, form):
        prisme = Prisme()
        if prisme.mock:
            return ['1234']
        data = form if type(form) == dict else form.cleaned_data
        claimant = data['fordringshaver'] or self.claimant_ids[0]
        impairment = PrismeImpairmentRequest(
            # claimant_id=self.get_claimant_id(self.request),
            claimant_id=claimant,
            cpr_cvr=data.get('debitor'),
            claim_ref=data.get('ekstern_sagsnummer'),
            amount_balance=-abs(data.get('beloeb', 0)),
            claim_number_seq=data.get('sekvensnummer')
        )
        return [x.rec_id for x in prisme.process_service(impairment, 'nedskrivning', self.cpr, self.cvr)]

    def form_valid(self, form):
        if len(self.claimant_ids) == 0:
            form.add_error(None, ValidationError(_("login.error_no_claimants"), 'login.error_no_claimants'))
            return self.form_invalid(form)
        pdf_id = None
        try:
            rec_ids = self.send_impairment(form)
            if rec_ids:
                pdf_id = self.store_pdf_context([{**form.cleaned_data, 'rec_ids': rec_ids}])
            return TemplateResponse(
                request=self.request,
                template="aka/impairment/success.html",
                context={
                    'rec_ids': rec_ids,
                    'upload': False,
                    'pdf_id': pdf_id,
                },
                using=self.template_engine
            )
        except PrismeException as e:
            if e.code == 250 or e.code == '250':
                form.add_error(None, e.as_validationerror)
                return self.form_invalid(form)
            logger.info("Got error code %s from prisme" % str(e.code))
            raise e

    def store_pdf_context(self, data):
        now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        pdf_context = {
            'received_date': date.today(),
            'cvr': self.cvr,
            'lines': [
                {
                    'debitor': subdata.get('debitor'),
                    'ekstern_sagsnummer': subdata.get('ekstern_sagsnummer'),
                    'beloeb': -abs(subdata.get('beloeb', 0)),
                    'sekvensnummer': subdata.get('sekvensnummer'),
                    'rec_ids': subdata.get('rec_ids')
                }
                for subdata in data
            ]
        }
        session = self.request.session
        if 'receipts' not in session:
            session['receipts'] = {}
        pdf_id = str(uuid.uuid4())
        session['receipts'][pdf_id] = {
            'context': pdf_context,
            'filename': f'kvittering_nedskrivning_{now}.pdf',
            'template': 'aka/impairment/receipt.html',
        }
        session.modified = True
        return pdf_id


class NedskrivningReceiptView(GetReceiptView):
    context = 'nedskrivning'


class NedskrivningUploadView(NedskrivningView):
    form_class = NedskrivningUploadForm
    template_name = 'aka/impairment/upload.html'
    parallel = False

    def handle_form(self, data):
        try:
            rec_ids = self.send_impairment(data)
            return {'rec_ids': rec_ids, **data}
        except PrismeException as e:
            logger.info("Got error from prisme: %s %s for %s" % (str(e.code), e.text, str(data)))
            return {'error': e}

    def form_valid(self, form):
        if self.parallel:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                results = list(executor.map(self.handle_form, [subform.cleaned_data for subform in form.subforms]))
        else:
            results = [self.handle_form(subform.cleaned_data) for subform in form.subforms]

        rec_ids = []
        responses = []
        errors = []
        for result in results:
            if 'rec_ids' in result:
                rec_ids += result['rec_ids']
                responses.append(result)
            if 'error' in result:
                errors.append(result['error'].as_error_dict)

        pdf_id = None
        if responses:
            pdf_id = self.store_pdf_context(responses)

        return TemplateResponse(
            request=self.request,
            template="aka/impairment/success.html",
            context={
                'rec_ids': rec_ids,
                'errors': errors,
                'upload': True,
                'pdf_id': pdf_id,
            },
            using=self.template_engine
        )


# NY18

@method_decorator(csrf_exempt, name='dispatch')
class RenteNotaView(RequireCvrMixin, IsContentMixin, SimpleGetFormMixin, PdfRendererMixin, JsonRendererMixin, SpreadsheetRendererMixin, TemplateView):
    form_class = InterestNoteForm
    template_name = 'aka/interestnote/interestnote.html'
    pdf_template_name = 'aka/interestnote/interestnote_pdf.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = []
        self.items = []

    def get_journal_fields(self):
        return [
            'updated',
            'account_number',
            'interest_note',
            'billing_classification'
        ]

    def get_transaction_fields(self):
        return [
            'voucher',
            'text',
            'due_date',
            'invoice_amount',
            'interest_amount',
            'transaction_date',
            'invoice',
            'calculate_from_date',
            'calculate_to_date',
            'interest_days',
        ]

    def get_fields(self) -> List[Field]:
        fields = [
            Field(name='updated', klass='nb'),
            Field(name='account_number', klass='nb'),
            Field(name='billing_classification', klass='nb'),
            Field(name='voucher', klass='nb'),
            Field(name='interest_note', klass='nb'),
            Field(name='text', klass=''),
            Field(name='due_date', klass='nb numbercell'),
            Field(name='invoice_amount', klass='nb numbercell', number=True),
            Field(name='interest_amount', klass='nb numbercell', number=True),
            Field(name='transaction_date', klass='nb numbercell'),
            Field(name='invoice', klass='nb'),
            Field(name='calculate_from_date', klass='nb numbercell'),
            Field(name='calculate_to_date', klass='nb numbercell'),
            Field(name='interest_days', klass='nb numbercell'),
        ]
        for field in fields:
            field.title = _("rentenota.%s" % field.name).replace("&shy;", "")
        return fields

    def load_items(self, form):
        prisme = Prisme()
        posts = []
        # Response is of type PrismeInterestNoteResponse
        # prisme.process_service handles mocking if necessary
        interest_note_data = prisme.process_service(
            PrismeInterestNoteRequest(self.cvr, form.cleaned_data['year'], form.cleaned_data['month']),
            'rentenota', self.cpr, self.cvr
        )

        for interest_note_response in interest_note_data:
            for journal in interest_note_response.interest_journal:
                journaldata = {
                    key: getattr(journal, key)
                    for key in self.get_journal_fields()
                }
                for transaction in journal.interest_transactions:
                    data = {
                        key: getattr(transaction, key)
                        for key in self.get_transaction_fields()
                    }
                    data.update(journaldata)
                    posts.append(data)
        self.items = posts

    def get_pages(self, key):
        return self.items

    def get_filename(self):
        return _("rentenota.filename").format(
            **dict(self.form.cleaned_data.items())
        )

    def get_sheetname(self):
        return "Rentenota"

    def get_rows(self):
        fields = self.get_fields()
        return [
            Row(cells=[
                Cell(field=field, value=item[field.name])
                for field in fields
            ])
            for item in self.items
        ]

    def form_valid(self, form):
        self.form = form
        try:
            self.load_items(form)
        except PrismeException as e:
            self.errors.append(e.as_error_dict)
        if 'format' in self.request.GET:
            response = self.render()
            if response is not None:
                return response
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = {
            'date': date.today().strftime('%d/%m/%Y'),
            'items': self.items,
            'rows': self.get_rows(),
            'fields': self.get_fields(),
            'total': sum([float(item['interest_amount']) for item in self.items])
            if self.items is not None else None,
            'errors': self.errors
        }
        context.update(kwargs)
        return super().get_context_data(**context)
