import logging
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from aka.rest.base import JSONRestView
from aka.helpers import validation
from aka.helpers.prisme import Prisme
from aka.helpers.result import Error, Success
from aka.helpers.sharedfiles import getSharedJson

logger = logging.getLogger(__name__)


class Nedskrivning(JSONRestView):
    '''This class handles the REST interface at /nedskrivning.
    '''

    def post(self, request, *args, **kwargs):
        '''
        POST handler.

        :param request: The request.
        :type request: HttpRequest.
        :returns: HttpResponse, HttpResponseBadRequest

        '''
        baseresponse = super().basepost(request)
        return baseresponse
