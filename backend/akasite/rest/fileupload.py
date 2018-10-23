from akasite.rest.base import JSONRestView
import json
from django.http import HttpResponse


class FileUpload(JSONRestView):
    def get(self, request, *args, **kwargs):
        dummyresponse = {"serversays": "Hello. You said FileUpload/GET"}
        return HttpResponse(json.dumps(dummyresponse),
                            content_type=JSONRestView.CT1)

    def post(self, request, *args, **kwargs):
        baseresponse = super().post(request, args, kwargs)

        if baseresponse.status_code == 200:
            self.data['serversays'] = "Hello. You said FileUpload/POST" # These 2 are only for test purposes.
            self.data['files'] = self.files # These 2 are only for test purposes.
            return HttpResponse(json.dumps(self.data),
                                content_type=JSONRestView.CT1)
        else:
            return baseresponse
