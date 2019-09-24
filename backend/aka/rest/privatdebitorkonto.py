import logging

# When the service is implemented unused imports should be removed,
# but until then they are just commented out as a reference
from django.http import JsonResponse, HttpResponse
from django.views import View

logger = logging.getLogger(__name__)


class Privatdebitorkonto(View):
    '''This class handles the REST interface at /privatdebitorkonto.
    '''

    def get(self, request, *args, **kwargs):
        '''
        GET handler.

        :param request: The request.
        :type request: HttpRequest.
        :returns: HttpResponse, HttpResponseBadRequest

        '''

        return JsonResponse("OK", safe=False)
