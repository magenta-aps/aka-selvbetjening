from akasite.rest.base import JSONRestView
import json
from django.http import HttpResponse


class FileUpload(JSONRestView):
    '''Class to handle files uploaded.

    This is part of the proof of concept.
    '''
    def get(self, request, *args, **kwargs):
        '''GET method.
        '''
        dummyresponse = {"serversays": "Hello. You said FileUpload/GET"}
        return HttpResponse(json.dumps(dummyresponse),
                            content_type=JSONRestView.CT1)

    def post(self, request, *args, **kwargs):
        '''POST method.
        '''
        baseresponse = super().post(request, args, kwargs)

        if baseresponse.status_code == 200:
            self.data['serversays'] = "Hello. You said FileUpload/POST"
            return HttpResponse(json.dumps(self.data),
                                content_type=JSONRestView.CT1)
        else:
            return baseresponse
