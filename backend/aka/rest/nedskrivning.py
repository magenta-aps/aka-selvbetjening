import logging

# When the service is implemented unused imports should be removed,
# but until then they are just commented out as a reference
from django.views.generic import FormView

logger = logging.getLogger(__name__)


class Nedskrivning(FormView):
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
