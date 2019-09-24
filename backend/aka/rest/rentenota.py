import logging
import os
from datetime import date

from aka.helpers.error import ErrorJsonResponse
from aka.helpers.prisme import Prisme
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseBadRequest
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
        :param year: The year for this rentenota.
        :type year: String (see pattern in URL dispatcher)
        :param month: The month for this rentenota.
        :type month: String (see pattern in URL dispatcher)
        :returns: HttpResponse of some variety.
        :raises: ValueError.
        '''

        try:
            year = int(year)
            month = int(month)
            logger.info(f'Get rentenota {year}-{month}')

            if month > 12 or month < 1:
                return ErrorJsonResponse.invalid_month()
            today = timezone.now()
            if year > today.year or (year == today.year and month >= today.month):
                return ErrorJsonResponse.future_month()

            prisme = Prisme(self.request)
            response = prisme.getRentenota(year, month)
            return JsonResponse(response)

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
