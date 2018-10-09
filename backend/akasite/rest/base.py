from django.views.generic import TemplateView
from django.views import View
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
import json


class ContentTypeError(Exception):
    """Exception raised for errors in the content-type
       of the request.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


class JSONRestView(View):
    CONTENT_TYPE = 'application/json'
    CONTENT_FILETYPE = 'multipart/form-data'

    def handle_uploaded_file(f):
        with open('some/file/name.txt', 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    def getContenttype(self, contenttypevalue):
        '''
        ------------------------------------------------------------
        Get content_type, charset etc from Content-Type header string.
        Input: The value of the 'CONTENT_TYPE' key in request.META.
               Expects something like this: 'type/subtype [; charset=xyz]'
        Output: Dict with 2 keys guaranteed present: 'type' and 'charset'.
                They may have no values, though.
                The key 'type' contains the type/subtype part of
                content_type (i.e. the main element).
        ------------------------------------------------------------
        '''
        result = {'type': '', 'charset': ''}

        first = contenttypevalue.split(';')

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

        Content-type must equal CONTENT_TYPE.
        charset must have a value.
        ------------------------------------------------------------
        '''

        self.payload = None

        try:
            # Check size of request?
            if 'CONTENT_TYPE' in request.META:
                contenttype = self.getContenttype(request.META['CONTENT_TYPE'])
            else:
                raise ContentTypeError('No content_type in request.')

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
        except (ContentTypeError, json.decoder.JSONDecodeError) as e:
            retval = HttpResponseBadRequest(
                     self.errorResponse(type(e).__name__ + ': {0}'.format(e)),
                     content_type=JSONRestView.CONTENT_TYPE)

        return retval

    def postfiles(self, request, *args, **kwargs):
        '''
        ------------------------------------------------------------
        Base class for POST handler.
        Input: Request.
        Output: HTTP Response of some variety.

        Content-type must equal CONTENT_TYPE.
        charset must have a value.
        ------------------------------------------------------------
        '''

        self.payload = None
        self.payload = {}

        try:
            # Check size of request?
            if 'CONTENT_TYPE' in request.META:
                contenttype = self.getContenttype(request.META['CONTENT_TYPE'])
            else:
                raise ContentTypeError('No content_type in request.')

            self.payload['AKA-Bruger'] = request.META['HTTP_X_AKA_BRUGER']

            if contenttype['type'].lower() != \
               JSONRestView.CONTENT_TYPE.lower():
                raise ContentTypeError('Contenttype must be ' +
                                       JSONRestView.CONTENT_TYPE +
                                       ', not ' + contenttype['type'])
            elif contenttype['charset'] in ['', None]:
                raise ContentTypeError('Charset is missing.')

            bdy = request.body.decode(contenttype['charset'])
            self.payload['bodysize'] = str(len(bdy))
            retval = HttpResponse()
        except (ContentTypeError, json.decoder.JSONDecodeError) as e:
            retval = HttpResponseBadRequest(
                     self.errorResponse(type(e).__name__ + ': {0}'.format(e)),
                     content_type=JSONRestView.CONTENT_TYPE)

        return retval

