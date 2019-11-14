import csv
import json
import logging
from io import StringIO

import chardet
from aka.clients.dafo import Dafo
from aka.clients.prisme import Prisme,PrismeException, PrismeNotFoundException
from aka.clients.prisme import PrismeClaimRequest
from aka.clients.prisme import PrismeInterestNoteRequest
from aka.clients.prisme import PrismeImpairmentRequest
from aka.clients.prisme import PrismePayrollRequest, PrismePayrollRequestLine
from aka.exceptions import AccessDeniedException
from aka.forms import InkassoForm, InkassoUploadForm, NedskrivningForm
from aka.forms import LoentraekForm
from aka.forms import LoentraekFormItem
from aka.forms import NedskrivningUploadForm
from aka.mixins import ErrorHandlerMixin
from aka.utils import ErrorJsonResponse, AccessDeniedJsonResponse
from django.conf import settings
from django.forms import formset_factory
from django.http import JsonResponse, HttpResponse
from django.template import Engine, Context
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils import translation
from django.utils.datetime_safe import date
from django.utils.decorators import method_decorator
from django.utils.translation.trans_real import DjangoTranslation
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, BaseFormView
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


class FordringshaverkontoView(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse("OK", safe=False)


class InkassoSagView(BaseFormView):

    form_class = InkassoForm

    def get(self, *args, **kwargs):
        return self.http_method_not_allowed(*args, **kwargs)

    def form_valid(self, form):
        prisme = Prisme()

        def get_codebtors(data):
            codebtors = []
            for i in range(1, 1000):
                if "meddebitor%d_cpr" % i in data:
                    codebtors.append(data["meddebitor%d_cpr" % i])
                elif "meddebitor%d_cvr" % i in data:
                    codebtors.append(data["meddebitor%d_cvr" % i])
                else:
                    break
            return codebtors

        claim = PrismeClaimRequest(
            claimant_id=form.cleaned_data.get('fordringshaver'),
            cpr_cvr=form.cleaned_data.get('debitor'),
            external_claimant=form.cleaned_data.get('fordringshaver2'),
            claim_group_number=form.cleaned_data.get('fordringsgruppe'),
            claim_type=form.cleaned_data.get('fordringstype'),
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
            codebtors=get_codebtors(form.cleaned_data),
            files=[file for name, file in form.files.items()]
        )
        try:
            prisme_reply = prisme.process_service(claim)[0]
            response = {
                'rec_id': prisme_reply.rec_id
            }
            return JsonResponse(response)
        except Exception as e:
            return ErrorJsonResponse.from_exception(e)

    def form_invalid(self, form):
        return ErrorJsonResponse.from_error_dict(form.errors)


class InkassoSagUploadView(InkassoSagView):
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
                subform = InkassoForm(data=row)
                if subform.is_valid():
                    response = super(InkassoSagUploadView, self).form_valid(subform)
                    responses.append(json.loads(response.content))
                else:
                    return ErrorJsonResponse.from_error_dict(subform.errors)
        except csv.Error as e:
            return ErrorJsonResponse.from_error_id('failed_reading_csv')
        return JsonResponse(responses, safe=False)

    def form_invalid(self, form):
        return ErrorJsonResponse.from_error_dict(form.errors)


class LoenTraekView(FormSetView, FormView):

    form_class = LoentraekForm
    template_name = 'aka/payrollForm.html'

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

        ####
        self.request.session['user_info'] = {'CVR': '12479182'}  # 12479182
        ####

        if 'user_info' not in self.request.session:
            raise AccessDeniedException('no_cvr')

        try:
            payroll = PrismePayrollRequest(
                cvr=self.request.session['user_info']['CVR'],
                date=date(int(form.cleaned_data['year']), int(form.cleaned_data['month']), 1),
                received_date=date.today(),
                amount=form.cleaned_data['total_amount'],
                lines=[
                    PrismePayrollRequestLine(
                        subform.cleaned_data.get('cpr_cvr'),
                        subform.cleaned_data.get('agreement_number'),
                        subform.cleaned_data.get('amount'),
                        subform.cleaned_data.get('net_salary')
                    ) for subform in formset
                ]
            )
            rec_id = prisme.process_service(payroll)[0].rec_id
            return TemplateResponse(
                request=self.request,
                template="aka/payrollSuccess.html",
                context={
                    'rec_ids': [rec_id]
                },
                using=self.template_engine
            )
        except PrismeException as e:
            print(e.code)
            raise e

    def form_invalid(self, form, formset):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )


class LoenTraekDistributionView(View):

    def get(self, request, cvrnumber, *args, **kwargs):
        data = [{'cprnumber': '1234567890',
                 'aftalenummer': '15934',
                 'lontraek': '1500',
                 'nettolon': '15000'
                 }]
        return JsonResponse(data, safe=False)


class NedskrivningView(ErrorHandlerMixin, FormView):

    form_class = NedskrivningForm
    template_name = 'aka/impairmentForm.html'

    def get_claimant_id(self, request):
        claimant_id = request.session['user_info'].get('claimant_id')
        if claimant_id is None:
            prisme = Prisme()
            try:
                claimant_id = prisme.check_cvr(request.session['user_info'].get('CVR'))
            except PrismeNotFoundException as e:
                raise AccessDeniedException(e.error_code, **e.params)
            request.session['user_info']['claimant_id'] = claimant_id
        return claimant_id

    def get(self, request, *args, **kwargs):
        ####
        self.request.session['user_info'] = {'CVR': '12479182'}  # 12479182
        ####
        self.get_claimant_id(request)
        return super(NedskrivningView, self).get(request, *args, **kwargs)

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

        ####
        self.request.session['user_info'] = {'CVR': '12479182'}  # 12479182
        ####

        if 'user_info' not in self.request.session:
            raise AccessDeniedException('no_cvr')

        try:
            rec_id = self.send_impairment(form, prisme)
            return TemplateResponse(
                request=self.request,
                template="aka/impairmentSuccess.html",
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
    template_name = 'aka/uploadImpairmentForm.html'

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
            template="aka/impairmentSuccess.html",
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


class RenteNotaView(View):

    def get(self, request, year, month, *args, **kwargs):
        '''Get rentenota data for the given interval.

        :param request: Djangos request object.
        :type request: Request object
        :param cvr: The CVR number of the subject
        :type cvr: eight digits
        :param year: The year for this rentenota.
        :type year: four digits
        :param month: The month for this rentenota.
        :type month: two digits
        :returns: HttpResponse of some variety.
        :raises: ValueError.
        '''

        try:
            if 'user_info' not in request.session:
                return AccessDeniedJsonResponse()
            else:
                user_info = request.session['user_info']
                cvr = user_info.get('CVR')
                cpr = user_info.get('CPR')

            year = int(year)
            month = int(month)
            logger.info(f'Get rentenota {year}-{month}')

            if month > 12 or month < 1:
                return ErrorJsonResponse.invalid_month()
            today = timezone.now()
            if year > today.year or (year == today.year and month > today.month):
                return ErrorJsonResponse.future_month()

            if cvr is not None:
                customer_data = Dafo().lookup_cvr(cvr)
            # elif cpr is not None:
            #     customer_data = Dafo().lookup_cpr(cpr)

            prisme = Prisme()

            posts = []
            # Response is of type PrismeInterestNoteResponse
            interest_note_data = prisme.process_service(
                PrismeInterestNoteRequest(cvr, year, month)
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

            land_map = {
                'GL': 'Grønland',
                'DK': 'Danmark'
            }

            return JsonResponse({
                'firmanavn': customer_data['navn'],
                'adresse': {
                    'gade': customer_data['adresse'],
                    'postnr': customer_data['postnummer'],
                    'by': customer_data['bynavn'],
                    'land': land_map[customer_data['landekode']],
                },
                'poster': posts
            })

        except Exception as e:
            logger.error(str(e))
            return ErrorJsonResponse.from_exception(e)
