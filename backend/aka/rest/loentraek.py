import logging
from aka.rest.base import JSONRestView
from aka.helpers import validation
from aka.helpers.prisme import Prisme
from aka.helpers.validation import Error, Success
from aka.helpers.sharedfiles import getSharedJson

logger = logging.getLogger(__name__)


class LoenTraek(JSONRestView):
    '''This class handles the REST interface at /loentraek

    The purpose is to report pay deductions to Prisme.
    '''

    def post(self, request, *args, **kwargs):
        '''
        POST handler.

        :param request: The request.
        :type request: HttpRequest.
        :returns: HttpResponse, HttpResponseBadRequest

        '''
        baseresponse = super().basepost(request)

        if baseresponse.status_code == 200:
            logger.debug(self.data)
            res = validation.validateRequired(['cvrnummer',
                                               'traekmaaned',
                                               'traekaar'],
                                              self.data)

            if res.status:
                prisme = Prisme()
                pres = prisme.sendToPrisme(self.data)
                return self.successResponse('Prisme says OK.')
            else:
                return res.toHttpResponse()
        else:
            return baseresponse
