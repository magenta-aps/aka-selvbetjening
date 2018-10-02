#from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import sys

class JSONRestView(View):
    def post(self, request, *args, **kwargs):
        '''
        ???
        if 'CONTENT_TYPE' in request.META:
            result.append('Content-Type=' + request.META['CONTENT_TYPE'] + '\n')
        '''

        try:
            # Check size?
            # Check MIMEType & charset?
            # Generelt: Hvad gør jeg hvis JSON er tom eller ulovlig?
            # Hvordan kommunikere status til subklasser?
            #
            bdy = request.body.decode('utf-8')
            self.payload = json.loads(bdy)
            retval = HttpResponse('Done.')
        except json.decoder.JSONDecodeError as err:
            self.payload = None
            retval = HttpResponseBadRequest('JSONDecodeError. {0}'.format(err))
        except:
            self.payload = None
            retval = HttpResponseBadRequest('Unexpected error: ' + sys.exc_info()[0].__name__)

        return retval



@method_decorator(ensure_csrf_cookie, name='dispatch')
class InkassoSagView(JSONRestView):
    def get(self, request, *args, **kwargs):
        return HttpResponse('You said GET.')

    def post(self, request, *args, **kwargs):
        baseresponse = super().post(request, args, kwargs)

        print(baseresponse.status_code)

        if baseresponse.status_code == 200:
            return HttpResponse('You said POST. JSON=[' + json.dumps(self.payload) + ']')
        else:
            return baseresponse
