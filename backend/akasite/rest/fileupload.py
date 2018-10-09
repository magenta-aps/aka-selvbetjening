from akasite.rest.base import JSONRestView
import json
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator


@method_decorator(ensure_csrf_cookie, name='dispatch')
class FileUpload(JSONRestView):
    def get(self, request, *args, **kwargs):
        dummyresponse = {"serversays": "Hello. You said FileUpload/GET"}
        return HttpResponse(json.dumps(dummyresponse),
                            content_type=JSONRestView.CT1)

    def post(self, request, *args, **kwargs):
        baseresponse = super().postfile(request, args, kwargs)

        if baseresponse.status_code == 200:
            self.payload['serversays'] = "Hello. You said FileUpload/POST"
            return HttpResponse(json.dumps(self.payload),
                                content_type=JSONRestView.CT1)
        else:
            return baseresponse
