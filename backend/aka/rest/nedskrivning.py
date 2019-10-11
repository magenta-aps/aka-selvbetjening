import logging

# When the service is implemented unused imports should be removed,
# but until then they are just commented out as a reference
from django.http import JsonResponse
from django.views import View

logger = logging.getLogger(__name__)


class Nedskrivning(View):
    '''This class handles the REST interface at /nedskrivning.
    '''

    def get(self, *args, **kwargs):
        return self.http_method_not_allowed(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        return JsonResponse("OK", safe=False)
