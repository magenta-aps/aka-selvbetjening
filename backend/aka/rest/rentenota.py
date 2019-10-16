import logging
import os

from aka.helpers.dafo import Dafo
from aka.helpers.error import ErrorJsonResponse
from aka.helpers.prisme import Prisme
from aka.helpers.prisme import PrismeInterestNoteRequest
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views import View

logger = logging.getLogger(__name__)


class RenteNota(View):
    '''This class handles the REST interface at /rentenota.
    '''

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
                # return AccessDeniedJsonResponse()
                cvr = '12345678'
                cpr = '1234567890'
            else:
                user_info = request.session['user_info']
                cvr = user_info.get('cvr')
                cpr = user_info.get('cpr')

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
            elif cpr is not None:
                customer_data = Dafo().lookup_cpr(cpr)

            prisme = Prisme(self.request)

            posts = []
            # Response is of type PrismeInterestNoteResponse
            try:
                interest_note_data = prisme.get_interest_note(
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


    ## Not really sure why this is here
    def fetch(self, request, *args, **kwargs):
        '''
        As a test, this method expects '?f=url' in the request.
        It will then download the resource, store it locally
        and pass it on to the caller.

        How to get the url in real life?
        How to get the contenttype in real life
        '''

        prisme = Prisme()
        # url = prisme.receiveFromPrisme(None)
        url = request.GET.get('f', '')
        filename = url.split('/')[-1]
        filefetched = prisme.fetchPrismeFile(url, settings.MEDIA_URL+filename)

        if filefetched:
            contenttype = 'application/pdf'  # How to get this in real life?
            path = settings.MEDIA_URL+filename
            with open(path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type=contenttype)
                cd = 'inline; filename=' + os.path.basename(path)
                response['Content-Disposition'] = cd
                return response
