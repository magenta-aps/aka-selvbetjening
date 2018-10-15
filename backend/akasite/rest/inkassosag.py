from akasite.rest.base import JSONRestView
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
import json
import logging

logger = logging.getLogger(__name__)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class InkassoSag(JSONRestView):
    def get(self, request, *args, **kwargs):
        dummyresponse = {"serversays": "Hello. You said InkassoSag/GET"}

        return HttpResponse(json.dumps(dummyresponse),
                            content_type=JSONRestView.RESTCONTENTTYPE)

    def post(self, request, *args, **kwargs):
        baseresponse = super().post(request, args, kwargs)


        if baseresponse.status_code == 200:

            logger.debug(self.payload)
            return HttpResponse(200)
        else:
            return baseresponse



