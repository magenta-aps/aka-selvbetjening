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
    Originally created as an endpoint for use in solution 6.2.
    '''

    def post(self, request, *args, **kwargs):
        '''
        Method for POST handler at /loentraek

        :param request: The request.
        :type request: HttpRequest.
        :returns: HttpResponse, HttpResponseBadRequest

        '''
        baseresponse = super().basepost(request)

        if baseresponse.status_code == 200:
            logger.debug(self.data)
            res = validation.validateRequired(['cvrnummer'], self.data)
        else:
            return baseresponse
