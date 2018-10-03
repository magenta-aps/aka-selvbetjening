#from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from v1.JSONBase import JSONRestView
import json
import sys

@method_decorator(ensure_csrf_cookie, name='dispatch')
class DebitorView(JSONRestView):
    def get(self, request, *args, **kwargs):
        dummyresponse = {"serversays" : "Hello, this is Debitor. You said GET" }
        return HttpResponse(json.dumps(dummyresponse), content_type='application/json')

    def post(self, request, *args, **kwargs):
        baseresponse = super().post(request, args, kwargs)

        if baseresponse.status_code == 200:
            dummyresponse = {"serversays" : "Hello, this is Debitor. You said POST"}
            return HttpResponse(json.dumps(dummyresponse), content_type='application/json')
        else:
            return baseresponse
