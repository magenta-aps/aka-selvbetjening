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

    It implements a POST endpoint. It should not be called directly,
    but is instead called by Django's url handler.
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
            result = validateInkassoJson(self.data).toHttpResponse()
        else:
            return baseresponse

def validateInkassoJson(reqJson):
    '''Validate a dict data-structure for the /loentraekdistribution endpoint

    :param reqJson: The Json to be validated
    :type reqJson: Dict
    :returns: Error, Success

    '''
    __REQUIRED_FIELDS = ['gernummer']
    return validation.validateRequired(__REQUIRED_FIELDS, reqJson)
