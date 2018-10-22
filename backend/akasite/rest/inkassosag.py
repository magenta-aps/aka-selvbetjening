from akasite.rest.base import JSONRestView
import json
from django.http import HttpResponse


class Schema(JSONRestView):
    def get(self, request, *args, **kwargs):
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'year': {'type': 'number'},
                'cpr': {'type': 'string', 'pattern': '^[0-9]{6}-[0-9]{4}$'},
                'height': {'type': 'number'},
            },
            'required': ['name', 'year', 'cpr'],
        }

        return HttpResponse(json.dumps(schema), content_type=JSONRestView.CT1)


class InkassoSag(JSONRestView):
    def get(self, request, *args, **kwargs):
        dummyresponse = {"serversays": "Hello. You said InkassoSag/GET"}
        return HttpResponse(json.dumps(dummyresponse),
                            content_type=JSONRestView.CT1)

    def post(self, request, *args, **kwargs):
        baseresponse = super().post(request, args, kwargs)

        if baseresponse.status_code == 200:
            self.payload["serversays"] = "Hello. You said InkassoSag/POST"
            return HttpResponse(json.dumps(self.payload),
                                content_type=JSONRestView.CT1)
        else:
            return baseresponse
