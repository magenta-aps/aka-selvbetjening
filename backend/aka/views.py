import csv
import json
import logging
import os
import re
from io import StringIO

import chardet
from aka.clients.dafo import Dafo
from aka.clients.prisme import Prisme, PrismeException, PrismeNotFoundException
from aka.clients.prisme import PrismeClaimRequest
from aka.clients.prisme import PrismeImpairmentRequest
from aka.clients.prisme import PrismeInterestNoteRequest
from aka.clients.prisme import PrismePayrollRequest, PrismePayrollRequestLine
from aka.exceptions import AccessDeniedException
from aka.forms import InkassoCoDebitorFormItem
from aka.forms import InkassoForm, InkassoUploadForm
from aka.forms import InterestNoteForm
from aka.forms import LoentraekForm, LoentraekUploadForm, LoentraekFormItem
from aka.forms import NedskrivningForm, NedskrivningUploadForm
from aka.mixins import ErrorHandlerMixin
from aka.mixins import RequireCvrMixin
from aka.utils import ErrorJsonResponse
from aka.utils import dummy_management_form
from aka.utils import format_filesize
from aka.utils import list_lstrip
from aka.utils import list_rstrip
from django.conf import settings
from django.forms import formset_factory
from django.http import JsonResponse, HttpResponse, FileResponse
from django.template import Engine, Context
from django.template.response import TemplateResponse
from django.utils import translation
from django.utils.datetime_safe import date
from django.utils.decorators import method_decorator
from django.utils.translation.trans_real import DjangoTranslation
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
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
        context['catalog_str'] = json.dumps(context['catalog'], sort_keys=True, indent=2) if context['catalog'] else None
        context['formats_str'] = json.dumps(context['formats'], sort_keys=True, indent=2)
        return context

    def render_to_response(self, context, **response_kwargs):
        template = Engine().from_string(self.js_catalog_template)
        return HttpResponse(template.render(Context(context)), 'text/javascript; charset="utf-8"')


class SetLanguageView(View):
    def post(self, request, *args, **kwargs):
        language = request.POST.get('language', settings.LANGUAGE_CODE)
        translation.activate(language)
        request.session[translation.LANGUAGE_SESSION_KEY] = language
        return JsonResponse("OK", safe=False)


logger = logging.getLogger(__name__)


class IndexTemplateView(TemplateView):
    template_name = 'index.html'

    @method_decorator(ensure_csrf_cookie)
    def get(self, *args, **kwargs):
        return super(IndexTemplateView, self).get(*args, **kwargs)


class VueTemplateView(TemplateView):
    template_name = 'vue.html'

    @method_decorator(ensure_csrf_cookie)
    def get(self, *args, **kwargs):
        return super(VueTemplateView, self).get(*args, **kwargs)


class ArbejdsgiverkontoView(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse("OK", safe=False)


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
        print(rootfolder)

        # Find root folder and all folders that match our configuration for the current cvr
        self.mounts = settings.MOUNTS['claimant_account_statements']
        subfolder_re = re.compile(self.mounts['subdir'].replace('{cvr}', self.cvr))
        companyfolders = [
            subfolder
            for subfolder in os.listdir(rootfolder)
            if os.path.isdir(os.path.join(rootfolder, subfolder))
            and subfolder_re.match(subfolder)
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
                    except:
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
    template_name = 'aka/claim/claimForm.html'

    def get_formset(self):
        return formset_factory(InkassoCoDebitorFormItem, **self.get_factory_kwargs())

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        formset = self.construct_formset()
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        return self.form_invalid(form, formset)

    @staticmethod
    def send_claim(form, formset):
        prisme = Prisme()

        codebtors = []
        for subform in formset:
            cpr = subform.cleaned_data.get("cpr")
            cvr = subform.cleaned_data.get("cvr")
            if cpr is not None:
                codebtors.append(cpr)
            elif cvr is not None:
                codebtors.append(cvr)

        claim_type = form.cleaned_data['fordringstype'].split(".")

        claim = PrismeClaimRequest(
            claimant_id=form.cleaned_data.get('fordringshaver'),
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
        prisme_reply = prisme.process_service(claim)[0]
        return prisme_reply

    def form_valid(self, form, formset):
        prisme_reply = self.send_claim(form, formset)
        return TemplateResponse(
            request=self.request,
            template="aka/payroll/payrollSuccess.html",
            context={
                'rec_ids': [prisme_reply.rec_id]
            },
            using=self.template_engine
        )

    def form_invalid(self, form, formset):
        return super().form_invalid(form)


class InkassoSagUploadView(RequireCvrMixin, FormView):
    form_class = InkassoUploadForm

    def form_valid(self, form):
        csv_file = form.cleaned_data['file']
        csv_file.seek(0)
        data = csv_file.read()
        charset = chardet.detect(data)
        responses = []
        try:
            csv_reader = csv.DictReader(StringIO(data.decode(charset['encoding'])))
            for row in csv_reader:
                row['fordringsgruppe'], row['fordringstype'] = InkassoForm.convert_group_type_text(row.get('fordringsgruppe'), row.get('fordringstype'))
                data = dummy_management_form("form")
                data.update(row)
                subform = InkassoForm(data=data)
                if subform.is_valid():
                    prisme_reply = InkassoSagView.send_claim(subform, [])
                    responses.append(prisme_reply.rec_id)
                else:
                    return ErrorJsonResponse.from_error_dict(subform.errors)
        except csv.Error as e:
            return ErrorJsonResponse.from_error_id('failed_reading_csv')
        return TemplateResponse(
            request=self.request,
            template="aka/payroll/payrollSuccess.html",
            context={
                'rec_ids': responses
            },
            using=self.template_engine
        )

    def form_invalid(self, form):
        return ErrorJsonResponse.from_error_dict(form.errors)


class LoentraekView(RequireCvrMixin, FormSetView, FormView):

    form_class = LoentraekForm
    template_name = 'aka/payroll/payrollForm.html'

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
            rec_id = prisme.process_service(payroll)[0].rec_id
            return TemplateResponse(
                request=self.request,
                template="aka/payroll/payrollSuccess.html",
                context={'rec_ids': [rec_id]},
                using=self.template_engine
            )
        except PrismeException as e:
            print(e.code)
            raise e

    def form_invalid(self, form, formset):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )


class LoentraekUploadView(LoentraekView):
    form_class = LoentraekUploadForm
    template_name = 'aka/payroll/uploadPayrollForm.html'

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
        return self.form_invalid(form)

    def form_invalid(self, form):
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


class NedskrivningView(ErrorHandlerMixin, RequireCvrMixin, FormView):

    form_class = NedskrivningForm
    template_name = 'aka/impairment/impairmentForm.html'

    def get_claimant_id(self, request):
        claimant_id = request.session['user_info'].get('claimant_id')
        if claimant_id is None:
            prisme = Prisme()
            try:
                claimant_id = prisme.check_cvr(self.cvr)
            except PrismeNotFoundException as e:
                raise AccessDeniedException(e.error_code, **e.params)
            request.session['user_info']['claimant_id'] = claimant_id
        return claimant_id

    def send_impairment(self, form, prisme):
        impairment = PrismeImpairmentRequest(
            claimant_id=self.get_claimant_id(self.request),
            cpr_cvr=form.cleaned_data.get('debitor'),
            claim_ref=form.cleaned_data.get('ekstern_sagsnummer'),
            amount_balance=-abs(form.cleaned_data.get('beloeb', 0)),
            claim_number_seq=form.cleaned_data.get('sekvensnummer')
        )
        return prisme.process_service(impairment)[0].rec_id

    def form_valid(self, form):
        prisme = Prisme()
        try:
            rec_id = self.send_impairment(form, prisme)
            return TemplateResponse(
                request=self.request,
                template="aka/impairment/impairmentSuccess.html",
                context={
                    'rec_ids': [rec_id]
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
    template_name = 'aka/impairment/uploadImpairmentForm.html'

    def form_valid(self, form):
        rec_ids = []
        prisme = Prisme()
        errors = []
        for subform in form.subforms:
            try:
                rec_ids.append(self.send_impairment(subform, prisme))
            except PrismeException as e:
                if e.code == 250:
                    errors.append({'key': 'nedskrivning.error_250', 'params': e.params})
                else:
                    raise e

        return TemplateResponse(
            request=self.request,
            template="aka/impairment/impairmentSuccess.html",
            context={
                'rec_ids': rec_ids,
                'errors': errors
            },
            using=self.template_engine
        )


class NetsopkraevningView(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse("OK", safe=False)


class PrivatdebitorkontoView(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse("OK", safe=False)


class RenteNotaView(RequireCvrMixin, FormView):
    form_class = InterestNoteForm
    template_name = 'aka/interestnote/interestnote.html'

    def __init__(self, *args, **kwargs):
        super(RenteNotaView, self).__init__(*args, **kwargs)
        self.posts = None

    def get_posts(self, form):
        prisme = Prisme()
        posts = []
        # Response is of type PrismeInterestNoteResponse
        interest_note_data = prisme.process_service(
            PrismeInterestNoteRequest(self.cvr, form.cleaned_data['year'], form.cleaned_data['month'])
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

    def form_valid(self, form):
        self.posts = self.get_posts(form)
        return TemplateResponse(
            request=self.request,
            template=self.template_name,
            context=self.get_context_data(),
            using=self.template_engine
        )

    def get_context_data(self, **kwargs):
        context = {
            'company': Dafo().lookup_cvr(self.cvr),
            'posts': self.posts,
            'total': sum([float(post['InterestAmount']) for post in self.posts])
            if self.posts is not None else None
        }
        context.update(kwargs)
        return super(RenteNotaView, self).get_context_data(**context)
