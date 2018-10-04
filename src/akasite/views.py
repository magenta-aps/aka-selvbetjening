from django.views.generic import TemplateView
from django.views import View
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
import json


class IndexView(TemplateView):
    template_name = 'akasite/index.html'


class Indberetning(TemplateView):
    template_name = 'akasite/indberet_fordring.html'


class ContentTypeError(Exception):
    """Exception raised for errors in the charset.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


class JSONRestView(View):
    CONTENT_TYPE = 'application/json'

    def getContenttype(self, requestMETA):
        '''
        ------------------------------------------------------------
        Get content_type.
        Input: The value of the 'CONTENT_TYPE' key in request.META.
               Expects something like this: 'type/subtype [; charset=xyz]'
        Output: Dict with 2 keys guaranteed present: 'type' and 'charset'.
                They may have no values, though.
                The key 'type' contains the type/subtype part of
                content_type (i.e. the main element).
        ------------------------------------------------------------
        '''
        result = {'type': '', 'charset': ''}

        if 'CONTENT_TYPE' not in requestMETA:
            raise ContentTypeError('No content_type in request.')

        first = requestMETA['CONTENT_TYPE'].split(';')

        for i in range(1, len(first)):
            if '=' in first[i]:
                param = first[i].strip().split('=')
                result[param[0].strip()] = param[1].strip()

        result['type'] = first[0].strip()

        return result

    def errorResponse(self, msg):
        '''
        ------------------------------------------------------------
        Compose error message.
        Input: String containing the message.
        Output: String that is a serialised JSON structure, with the
                error message incorporated.
        ------------------------------------------------------------
        '''
        return json.dumps({"status": "Request failed.", "message": msg})

    def post(self, request, *args, **kwargs):
        '''
        ------------------------------------------------------------
        Base class for POST handler.
        Input: Request.
        Output: HTTP Response of some variety.

        Content-type must equal CONTENT_TYPE (see below for what it is).
        charset must have a value.
        ------------------------------------------------------------
        '''

        self.payload = None

        try:
            # Check size of request?
            contenttype = self.getContenttype(request.META)

            if contenttype['type'].lower() != \
               JSONRestView.CONTENT_TYPE.lower():
                raise ContentTypeError('Contenttype must be ' +
                                       JSONRestView.CONTENT_TYPE +
                                       ', not ' + contenttype['type'])
            elif contenttype['charset'] in ['', None]:
                raise ContentTypeError('Charset is missing.')

            bdy = request.body.decode(contenttype['charset'])
            self.payload = json.loads(bdy)
            retval = HttpResponse()
        except json.decoder.JSONDecodeError as err:
            retval = HttpResponseBadRequest(
                     self.errorResponse('JSONDecodeError. {0}'.format(err)))
        except ContentTypeError as err:
            retval = HttpResponseBadRequest(
                     self.errorResponse('ContentTypeError. {0}'.format(err)))

        return retval


@method_decorator(ensure_csrf_cookie, name='dispatch')
class InkassoSag(JSONRestView):
    def get(self, request, *args, **kwargs):
        dummyresponse = {"serversays": "Hello. You said InkassoSag/GET"}
        return HttpResponse(json.dumps(dummyresponse),
                            content_type=JSONRestView.CONTENT_TYPE)

    def post(self, request, *args, **kwargs):
        baseresponse = super().post(request, args, kwargs)

        if baseresponse.status_code == 200:
            self.payload["serversays"] = "Hello. You said InkassoSag/POST"
            return HttpResponse(json.dumps(self.payload),
                                content_type=JSONRestView.CONTENT_TYPE)
        else:
            return baseresponse


@method_decorator(ensure_csrf_cookie, name='dispatch')
class Debitor(JSONRestView):
    def get(self, request, *args, **kwargs):
        dummyresponse = {"serversays": "Hello. You said Debitor/GET"}
        return HttpResponse(json.dumps(dummyresponse),
                            content_type=JSONRestView.CONTENT_TYPE)

    def post(self, request, *args, **kwargs):
        baseresponse = super().post(request, args, kwargs)

        if baseresponse.status_code == 200:
            self.payload["serversays"] = "Hello. You said Debitor/POST"
            return HttpResponse(json.dumps(self.payload),
                                content_type=JSONRestView.CONTENT_TYPE)
        else:
            return baseresponse
