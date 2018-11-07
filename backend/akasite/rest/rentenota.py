from akasite.rest.base import JSONRestView
from akasite.rest.prisme import Prisme
from akasite.rest.utils import AKAUtils
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotAllowed
from django.conf import settings
import logging
import os
import json

logger = logging.getLogger(__name__)


class RenteNota(JSONRestView):
    '''Handles calls for the Rentenota interface. Gets period data from Prisme.
    '''

    def initiatedownload(self, path, contenttype):
        with open(path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type=contenttype)
            cd = 'inline; filename=' + os.path.basename(path)
            response['Content-Disposition'] = cd
            return response

        return HttpResponseBadRequest

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
            return self.initiatedownload(settings.MEDIA_URL+filename,
                                         contenttype)

    def get(self, request, start, end, *args, **kwargs):
        '''Get rentenota data for the given interval.

        :param request: Djangos request object.
        :type request: Request object
        :param start: Start date of this rentenota.
        :type start: String with date pattern YYYYMMDD
        :param end: End date of this rentenota.
        :type end: String with date pattern YYYYMMDD
        :returns: HttpResponse of some variety.
        :raises: ValueError.
        '''

        try:
            fromdate = AKAUtils.datefromstring(start)
            todate = AKAUtils.datefromstring(end)
            if fromdate > todate:
                raise ValueError('Fromdate must be <= todate.')
        except ValueError as ve:
            logger.error(str(ve))
            return self.errorResponse(ve)

        try:
            prisme = Prisme()
            data = prisme.getRentenota(fromdate, todate)
        except Exception as e:
            logger.error(str(e))
            return self.errorResponse(e)

        logger.info('Get rentenota from ' + str(fromdate) + ' to ' + str(todate))

        return HttpResponse(json.dumps(data), content_type=JSONRestView.CT1)
