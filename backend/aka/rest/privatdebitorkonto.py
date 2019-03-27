import logging
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from aka.rest.base import JSONRestView
from aka.helpers import validation
from aka.helpers.prisme import Prisme
from aka.helpers.result import Error, Success
from aka.helpers.sharedfiles import getSharedJson

logger = logging.getLogger(__name__)


class Privatdebitorkonto(JSONRestView):
    '''This class handles the REST interface at /privatdebitorkonto.
    '''

    def get(self, request, *args, **kwargs):
        '''
        GET handler.

        :param request: The request.
        :type request: HttpRequest.
        :returns: HttpResponse, HttpResponseBadRequest

        '''

        return self.successResponse("OK")
