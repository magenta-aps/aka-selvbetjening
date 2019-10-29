import csv
import json
import logging
from io import StringIO

import chardet
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django.views.generic.edit import BaseFormView

from .clients.dafo import Dafo
from .clients.prisme import Prisme, PrismeClaimRequest, PrismeInterestNoteRequest
from .forms import InkassoForm, InkassoUploadForm
from .utils import ErrorJsonResponse, AccessDeniedJsonResponse

logger = logging.getLogger(__name__)

class IndexTemplateView(TemplateView):
    template_name = 'index.html'

    @method_decorator(ensure_csrf_cookie)
    def get(self, *args, **kwargs):
        return super(IndexTemplateView, self).get(*args, **kwargs)


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
        return JsonResponse({'rec_id': 1234})
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


class LoenTraekView(View):

    def get(self, *args, **kwargs):
        return self.http_method_not_allowed(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        return JsonResponse("OK", safe=False)


class LoenTraekDistributionView(View):

    def get(self, request, cvrnumber, *args, **kwargs):
        data = [{'cprnumber': '1234567890',
                 'aftalenummer': '15934',
                 'lontraek': '1500',
                 'nettolon': '15000'
                 }]
        return JsonResponse(data, safe=False)


class NedskrivningView(View):

    def post(self, request, *args, **kwargs):
        return JsonResponse("OK", safe=False)


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
            try:
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
            except Exception as e:
                print(e)

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
