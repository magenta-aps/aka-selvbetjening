import logging
# from django.http import HttpResponse
# from django.http import HttpResponseBadRequest
from aka.rest.base import JSONRestView
# from aka.helpers import validation
# from aka.helpers.prisme import Prisme
# from aka.helpers.result import Error, Success
# from aka.helpers.sharedfiles import getSharedJson

# When the service is implemented unused imports should be removed,
# but until then they are just commented out as a reference

logger = logging.getLogger(__name__)


class Fordringshaverkonto(JSONRestView):
    '''This class handles the REST interface at /fordringshaverkonto.
    '''

    def get(self, request, *args, **kwargs):
        '''
        GET handler.

        :param request: The request.
        :type request: HttpRequest.
        :returns: HttpResponse, HttpResponseBadRequest

        '''

        return self.successResponse("OK")
