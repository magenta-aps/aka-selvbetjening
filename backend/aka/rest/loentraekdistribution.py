import logging
import json
from django.http import HttpResponse

# Internal tools
from aka.rest.base import JSONRestView
# from aka.helpers import validation
# from aka.helpers.result import Error, Success
# from aka.helpers.sharedfiles import getSharedJson

# When the service is implemented unused imports should be removed,
# but until then they are just commented out as a reference

logger = logging.getLogger(__name__)


class LoenTraekDistribution(JSONRestView):
    '''This class handles the REST interface at /loentraekdistribution

    The purpose is to get the distribution of pay deductions that was
    used previously, to save the user time when doing loentraek.
    Originally created as an endpoint to help at endpoint /loentraek.
    '''

    def get(self, request, cvrnumber, *args, **kwargs):
        '''
        GET handler.

        :param request: The request.
        :type request: HttpRequest.
        :returns: HttpResponse, HttpResponseBadRequest

        '''

        data = [{'cprnumber': '1234567890',
                 'aftalenummer': '15934',
                 'lontraek': '1500',
                 'nettolon': '15000'
                 }]

        return HttpResponse(json.dumps(data), content_type=JSONRestView.CT1)
