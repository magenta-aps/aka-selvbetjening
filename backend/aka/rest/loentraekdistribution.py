import logging

# Internal tools
from aka.rest.base import JSONRestView
from aka.helpers import validation
from aka.helpers.validation import Error, Success
from aka.helpers.sharedfiles import getSharedJson

logger = logging.getLogger(__name__)


class LoenTraekDistribution(JSONRestView):
    '''This class handles the REST interface at /loentraekdistribution

    The purpose is to get the distribution of pay deductions that was
    used previously, to save the user time when doing loentraek.
    Originally created as an endpoint to help at endpoint /loentraek.
    '''

    def get(self, request, *args, **kwargs):
        '''
        GET handler.

        :param request: The request.
        :type request: HttpRequest.
        :returns: HttpResponse, HttpResponseBadRequest

        '''
        return self.successResponse("OK")
