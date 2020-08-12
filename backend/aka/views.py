import json
import logging
import os
import re

from aka.clients.dafo import Dafo
from aka.clients.prisme import Prisme, PrismeException
from aka.clients.prisme import PrismeCitizenAccountRequest
from aka.clients.prisme import PrismeClaimRequest
from aka.clients.prisme import PrismeEmployerAccountRequest
from aka.clients.prisme import PrismeImpairmentRequest
from aka.clients.prisme import PrismeInterestNoteRequest
from aka.clients.prisme import PrismePayrollRequest, PrismePayrollRequestLine
from aka.data.fordringsgruppe import groups
from aka.forms import InkassoCoDebitorFormItem
from aka.forms import InkassoForm, InkassoUploadForm
from aka.forms import InterestNoteForm
from aka.forms import KontoForm
from aka.forms import LoentraekForm, LoentraekUploadForm, LoentraekFormItem
from aka.forms import NedskrivningForm, NedskrivningUploadForm
from aka.mixins import ErrorHandlerMixin
from aka.mixins import HasUserMixin
from aka.mixins import PdfRendererMixin
from aka.mixins import JsonRendererMixin
from aka.mixins import RequireCprMixin
from aka.mixins import RequireCvrMixin
from aka.mixins import SimpleGetFormMixin
from aka.utils import format_filesize
from aka.utils import get_ordereddict_key_index
from aka.utils import list_lstrip
from aka.utils import list_rstrip
from aka.utils import spreadsheet_col_letter
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import formset_factory
from django.http import JsonResponse, HttpResponse, FileResponse
from django.template import Engine, Context
from django.template.response import TemplateResponse
from django.utils import translation
from django.utils.datetime_safe import date
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.utils.translation.trans_real import DjangoTranslation
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.views.i18n import JavaScriptCatalog
from extra_views import FormSetView
from sullissivik.login.nemid.nemid import NemId
from sullissivik.login.openid.openid import OpenId



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


logger = logging.getLogger(__name__)


class IndexTemplateView(HasUserMixin, TemplateView):
    template_name = 'index.html'

    @method_decorator(ensure_csrf_cookie)
    def get(self, *args, **kwargs):
        return super(IndexTemplateView, self).get(*args, **kwargs)


class LoginView(TemplateView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = {'back': self.request.GET.get('back')}
        context.update(kwargs)
        return super().get_context_data(**context)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        method = request.session.get('login_method')
        if method == 'openid':
            return OpenId.logout(self.request.session)
        else:
            return NemId.logout(self.request.session)


@method_decorator(csrf_exempt, name='dispatch')
class KontoView(SimpleGetFormMixin, PdfRendererMixin, JsonRendererMixin, TemplateView):

    form_class = KontoForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = None

    def form_valid(self, form):
        self.form = form
        try:
            self.items = self.get_items(form)
        except PrismeException as e:
            form.add_error(None, e.as_validationerror)
            return self.form_invalid(form)
        if 'format' in self.request.GET:
            response = self.render()
            if response is not None:
                return response
        return super(KontoView, self).form_valid(form)


    def get_context_data(self, **kwargs):
        context = {}
        if self.form.is_bound:
            formdata = self.form.cleaned_data
            fields = self.get_fields()
            if self.request.GET.get('format') == 'pdf':
                fields = [
                    field for field in fields
                    if field not in formdata['hidden']
                ]

            context.update({
                'items': self.items,
                'date': date.today().strftime('%d/%m/%Y'),
                'sum': sum([item.amount for item in self.items]) if self.items else 0,
                'period': {
                    'from_date': formdata['from_date'].strftime('%d-%m-%Y') if formdata.get('from_date') is not None else None,
                    'to_date': formdata['to_date'].strftime('%d-%m-%Y') if formdata.get('to_date') is not None else None
                },
                'fields': fields
            })
        context.update(kwargs)
        return super().get_context_data(**context)


# NY16
class ArbejdsgiverKontoView(RequireCvrMixin, KontoView):

    template_name = 'aka/employer_account/account.html'

    def get_pdf_filename(self):
        try:
            from_date = self.form.cleaned_data['from_date'].strftime('%Y-%m-%d')
        except:
            from_date = "alle"
        try:
            to_date = self.form.cleaned_data['to_date'].strftime('%Y-%m-%d')
        except:
            to_date = "alle"
        return _("employeraccount.filename").format(
            from_date=from_date,
            to_date=to_date
        )

    def get_items(self, form):
        prisme = Prisme()
        account_request = PrismeEmployerAccountRequest(
            self.cvr,
            form.cleaned_data['from_date'],
            form.cleaned_data['to_date'],
            form.cleaned_data['open_closed']
        )
        prisme_reply = prisme.process_service(account_request, 'arbejdsgiverkonto')[0]
        return prisme_reply

    def get_fields(self):
        return [
            {'name': 'account_number', 'class': 'nb'},
            {'name': 'transaction_date', 'class': 'nb'},
            {'name': 'accounting_date', 'class': 'nb'},
            {'name': 'debitor_group_id', 'class': 'nb'},
            {'name': 'debitor_group_name', 'class': 'nb'},
            {'name': 'voucher',  'class': 'nb'},
            {'name': 'text', 'class': ''},
            {'name': 'payment_code', 'class': 'nb'},
            {'name': 'payment_code_name', 'class': 'nb'},
            {'name': 'amount', 'class': 'nb', 'number': True},
            {'name': 'remaining_amount', 'class': 'nb', 'number': True},
            {'name': 'due_date', 'class': 'nb'},
            {'name': 'closed_date', 'class': 'nb'},
            {'name': 'last_settlement_voucher', 'class': 'nb'},
            {'name': 'collection_letter_date', 'class': 'nb'},
            {'name': 'collection_letter_code', 'class': 'nb'},
            {'name': 'claim_type_code', 'class': 'nb'},
            {'name': 'invoice_number', 'class': 'nb'},
            {'name': 'transaction_type', 'class': 'nb'},
            {'name': 'rate_number', 'class': 'nb'},
        ]

    def get_context_data(self, **kwargs):
        context = {
            'company': Dafo().lookup_cvr(self.cvr)
        }
        context.update(kwargs)
        return super().get_context_data(**context)


# S23

class BorgerKontoView(RequireCprMixin, KontoView):

    template_name = 'aka/citizen_account/account.html'

    def get_pdf_filename(self):
        try:
            from_date = self.form.cleaned_data['from_date'].strftime('%Y-%m-%d')
        except:
            from_date = "alle"
        try:
            to_date = self.form.cleaned_data['to_date'].strftime('%Y-%m-%d')
        except:
            to_date = "alle"
        return _("citizenaccount.filename").format(
            from_date=from_date,
            to_date=to_date
        )

    def get_items(self, form):
        prisme = Prisme()
        account_request = PrismeCitizenAccountRequest(
            self.cpr,
            form.cleaned_data['from_date'],
            form.cleaned_data['to_date'],
            form.cleaned_data['open_closed']
        )
        prisme_reply = prisme.process_service(account_request, 'borgerkonto')[0]
        return prisme_reply

    def get_fields(self):
        return [
            {'name':'account_number', 'class': 'nb'},
            {'name':'transaction_date', 'class': 'nb'},
            {'name':'accounting_date', 'class': 'nb'},
            {'name':'debitor_group_id', 'class': 'nb'},
            {'name':'debitor_group_name', 'class': 'nb'},
            {'name':'voucher', 'class': 'nb'},
            {'name':'text', 'class': ''},
            {'name':'payment_code', 'class': 'nb'},
            {'name':'payment_code_name', 'class': 'nb'},
            {'name':'amount', 'class': 'nb', 'number': True},
            {'name':'remaining_amount', 'class': 'nb', 'number': True},
            {'name':'due_date', 'class': 'nb'},
            {'name':'closed_date', 'class': 'nb'},
            {'name':'last_settlement_voucher', 'class': 'nb'},
            {'name':'collection_letter_date', 'class': 'nb'},
            {'name':'collection_letter_code', 'class': 'nb'},
            {'name':'claim_type_code', 'class': 'nb'},
            {'name':'invoice_number', 'class': 'nb'},
            {'name':'transaction_type', 'class': 'nb'},
            {'name':'claimant_name', 'class': 'nb'},
            {'name':'claimant_id', 'class': 'nb'},
            {'name':'child_claimant', 'class': 'nb'},
        ]


# 6.1

class FordringshaverkontoView(RequireCvrMixin, TemplateView):

    template_name = 'aka/claimant_account/list.html'

    @staticmethod
    def rootfolder():
        mounts = settings.MOUNTS['claimant_account_statements']
        return os.path.abspath(mounts['maindir'])

    def get(self, request, path=None, *args, **kwargs):

        # Clean path - it should become an array of path entries, empty if input is '/'
        if '..' in path.split('/'):
            raise FileNotFoundError(path)
        if path is None:
            path = []
        self.path = list_rstrip(path.split('/'), '')
        rootfolder = self.rootfolder()

        # Find root folder and all folders that match our configuration for the current cvr
        self.mounts = settings.MOUNTS['claimant_account_statements']
        subfolder_re = re.compile(self.mounts['subdir'].replace('{cvr}', self.cvr))
        companyfolders = [
            subfolder
            for subfolder in os.listdir(rootfolder)
            if os.path.isdir(os.path.join(rootfolder, subfolder)) and subfolder_re.match(subfolder)
        ]

        # Find folders that match our path in each companyfolder
        self.folders = []
        found = False
        self.relpath = os.path.join(*self.path) if self.path else None
        if companyfolders:
            for companyfolder in companyfolders:
                abs_path = os.path.join(*list_rstrip([rootfolder, companyfolder, self.relpath]))
                if os.path.isfile(abs_path):
                    # If we have a file, return it
                    return FileResponse(open(abs_path, 'rb'), as_attachment=True)
                try:
                    if os.path.isdir(abs_path):
                        found = True
                        self.folders.append(abs_path)
                except FileNotFoundError:
                    continue
            if not found:
                raise FileNotFoundError(path)

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        entries = []
        for abs_path in self.folders:
            folder_listing = os.listdir(abs_path)

            for filename in folder_listing:
                fullpath = os.path.join(abs_path, filename)
                entry = {
                    'name': filename,
                    'path': '/' + os.path.join(*list_lstrip([self.relpath, filename])).replace(os.path.pathsep, '/')
                }
                if os.path.isfile(fullpath):
                    entry['folder'] = False
                    entry['type'] = os.path.splitext(filename)[1].lstrip('.')
                    try:
                        bytesize = entry['size'] = os.path.getsize(fullpath)
                        entry['formatted_size'] = format_filesize(bytesize)
                    except Exception as e:
                        pass
                elif os.path.isdir(fullpath):
                    entry['folder'] = True
                    entry['size'] = len(os.listdir(fullpath))
                else:
                    continue
                entries.append(entry)
        entries.sort(key=lambda entry: entry['name'])
        parent_path = ('/' + os.path.join(*self.path[:-1])) if self.path else None
        context = {
            'path': self.relpath,
            'parent': parent_path,
            'entries': entries
        }
        context.update(**kwargs)
        return super().get_context_data(**context)


class InkassoSagView(RequireCvrMixin, FormSetView, FormView):

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
    def send_claim(claimant_id, form, formset=None, codebtors=None):
        prisme = Prisme()

        if codebtors is None:
            codebtors = []
        if formset:
            for subform in formset:
                cpr = subform.cleaned_data.get("cpr")
                cvr = subform.cleaned_data.get("cvr")
                if cpr is not None:
                    codebtors.append(cpr)
                elif cvr is not None:
                    codebtors.append(cvr)

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
        prisme_reply = prisme.process_service(claim, 'fordring')[0]
        return prisme_reply

    def form_valid(self, form, formset):
        prisme_reply = InkassoSagView.send_claim(self.claimant_ids[0], form, formset)
        return TemplateResponse(
            request=self.request,
            template="aka/claim/success.html",
            context={
                'rec_ids': [prisme_reply.rec_id],
                'upload': False
            },
            using=self.template_engine
        )

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))


class InkassoSagUploadView(RequireCvrMixin, FormView):
    form_class = InkassoUploadForm
    template_name = 'aka/claim/upload.html'

    def form_valid(self, form):
        responses = []
        codebtor_re = re.compile("^codebtor_\d+$")
        claimant_id = self.claimant_ids[0]
        for subform in form.subforms:
            codebtors = []
            for field, value in subform.cleaned_data.items():
                match = codebtor_re.match(field)
                if match and len(value):
                    codebtors.append(value)
            prisme_reply = InkassoSagView.send_claim(claimant_id, subform, codebtors=codebtors)
            responses.append(prisme_reply.rec_id)

        return TemplateResponse(
            request=self.request,
            template="aka/claim/success.html",
            context={
                'rec_ids': responses,
                'upload': True
            },
            using=self.template_engine
        )


class InkassoGroupDataView(View):
    def get(self, request, var='', *args, **kwargs):
        data = json.dumps(groups)
        if var:
            return HttpResponse("%s = %s" % (var, data), content_type='text/javascript')
        return HttpResponse(data, content_type='application/json')


# 6.2

class LoentraekView(RequireCvrMixin, FormSetView, FormView):

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
            rec_id = prisme.process_service(payroll, 'loentraek')[0].rec_id
            return TemplateResponse(
                request=self.request,
                template="aka/payroll/success.html",
                context={'rec_ids': [rec_id]},
                using=self.template_engine
            )
        except PrismeException as e:
            found = False
            if e.code == 250:
                d = e.as_error_dict
                if 'params' in d and 'nr' in d['params']:
                    for subform in formset:
                        if subform.cleaned_data.get('agreement_number') == d['params']['nr']:
                            subform.add_error('agreement_number', e.as_validationerror)
                            found = True
            if not found:
                form.add_error(None, e.as_validationerror)
            return self.form_invalid(form, formset)

    def form_invalid(self, form, formset):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )


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


class LoenTraekDistributionView(View):

    def get(self, request, cvrnumber, *args, **kwargs):
        data = [{'cprnumber': '1234567890',
                 'aftalenummer': '15934',
                 'lontraek': '1500',
                 'nettolon': '15000'
                 }]
        return JsonResponse(data, safe=False)


# 6.4

class NedskrivningView(ErrorHandlerMixin, RequireCvrMixin, FormView):

    form_class = NedskrivningForm
    template_name = 'aka/impairment/form.html'

    def send_impairment(self, form, prisme):
        impairment = PrismeImpairmentRequest(
            # claimant_id=self.get_claimant_id(self.request),
            claimant_id=self.claimant_ids[0],
            cpr_cvr=form.cleaned_data.get('debitor'),
            claim_ref=form.cleaned_data.get('ekstern_sagsnummer'),
            amount_balance=-abs(form.cleaned_data.get('beloeb', 0)),
            claim_number_seq=form.cleaned_data.get('sekvensnummer')
        )
        return prisme.process_service(impairment, 'nedskrivning')[0].rec_id

    def form_valid(self, form):
        prisme = Prisme()
        try:
            rec_id = self.send_impairment(form, prisme)
            return TemplateResponse(
                request=self.request,
                template="aka/impairment/success.html",
                context={
                    'rec_ids': [rec_id],
                    'upload': False
                },
                using=self.template_engine
            )
        except PrismeException as e:
            if e.code == 250:
                form.add_error('ekstern_sagsnummer', e.as_validationerror)
                return self.form_invalid(form)
            raise e


class NedskrivningUploadView(NedskrivningView):
    form_class = NedskrivningUploadForm
    template_name = 'aka/impairment/upload.html'

    def form_valid(self, form):
        rec_ids = []
        prisme = Prisme()
        errors = []
        for subform in form.subforms:
            try:
                rec_ids.append(self.send_impairment(subform, prisme))
            except PrismeException as e:
                if e.code == 250:
                    errors.append(e.as_error_dict)
                else:
                    raise e

        return TemplateResponse(
            request=self.request,
            template="aka/impairment/success.html",
            context={
                'rec_ids': rec_ids,
                'errors': errors,
                'upload': True
            },
            using=self.template_engine
        )


class NetsopkraevningView(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse("OK", safe=False)


class PrivatdebitorkontoView(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse("OK", safe=False)


# NY18

@method_decorator(csrf_exempt, name='dispatch')
class RenteNotaView(RequireCvrMixin, SimpleGetFormMixin, PdfRendererMixin, TemplateView):
    form_class = InterestNoteForm
    template_name = 'aka/interestnote/interestnote.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = []
        self.posts = None

    def get_posts(self, form):
        prisme = Prisme()
        posts = []
        # Response is of type PrismeInterestNoteResponse
        interest_note_data = prisme.process_service(
            PrismeInterestNoteRequest(self.cvr, form.cleaned_data['year'], form.cleaned_data['month']),
            'rentenota'
        )

        for interest_note_response in interest_note_data:
            for journal in interest_note_response.interest_journal:
                journaldata = {
                    k: v
                    for k, v in journal.data.items()
                    if k in [
                        'Updated', 'AccountNum', 'InterestNote',
                        'ToDate', 'BillingClassification'
                    ]
                }
                for transaction in journal.interest_transactions:
                    data = {}
                    data.update(transaction.data)
                    data.update(journaldata)
                    posts.append(data)
        return posts

    def get_pdf_filename(self):
        return _("rentenota.filename").format(
            **dict(self.form.cleaned_data.items())
        )

    def form_valid(self, form):
        self.form = form
        try:
            self.posts = self.get_posts(form)
        except PrismeException as e:
            self.errors.append(e.as_error_dict)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = {
            'date': date.today().strftime('%d/%m/%Y'),
            'posts': self.posts,
            'total': sum([float(post['InterestAmount']) for post in self.posts])
            if self.posts is not None else None,
            'errors': self.errors
        }
        context.update(kwargs)
        return super().get_context_data(**context)
