from aka.rest.base import JSONRestView
from aka.helpers.prisme import Prisme
from aka.helpers.result import Error, Success
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)


class RenteNota(JSONRestView):
    '''This class handles the REST interface at /rentenota.
    '''

    def initiatedownload(self, path, contenttype):
        '''
        Initiate a download of file at given path,
        with given contenttype.

        :param path: Full path to the file to be downloaded.
        :type path: String
        :param contenttype: Content type of the file to be downloaded.
        :type contenttype: String
        :returns: HttpResponse to send to the browser/frontend, so the
                  download can be started.
        '''

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
            prisme = Prisme()
            logger.info(f'Get rentenota {year}-{month}')

            return (validateInputDate(year, month)
                    .andThen(prisme.getRentenota)
                    .toHttpResponse()
                    )

        except Exception as e:
            logger.error(str(e))
            return self.errorResponse(e)


def validateInputDate(year, month):
    '''Validate that the input parameter is a valid month and year

    '''
    if month > 12 or month < 1:
        return Error('invalid_month')
    # elif year < 1900 or year > 2100:
    #     return Error('invalid year')
    else:
        return Success((year, month))
