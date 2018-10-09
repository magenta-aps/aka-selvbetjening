from django.views.generic import TemplateView
from django.views import View
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
import json
import random

class ContentTypeError(Exception):
    """Exception raised for errors in the content-type
       of the request.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


class JSONRestView(View):
    RESTCONTENTTYPE = 'application/json'
    UPLOADFILECONTENTTYPE = 'multipart/form-data'

    def tmpfilename(self):
        return ''.join([
            random.choice('abcdefghijklmnopqrstuvwxyz0123456789')
            for i in range(50)
            ])


    def handle_uploaded_file(self, f, destinationfilename):
        with open(destinationfilename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    def validContenttype(self, metadict, expectedcontenttype, charsetrequired=True):
        '''
        ------------------------------------------------------------
        Validate content_type and charset from Content-Type header string.
        Input: The request.META dict.
        Output: If all is OK, returns dict with 2 keys guaranteed 
                present: 'type' and 'charset'.
                They may have no values, though.
                The key 'type' contains the type/subtype part of
                content_type (i.e. the main element).

                If errors, i.e. missing or incorrect contenttype,
                raise ContentType exceptiom.
        ------------------------------------------------------------
        '''
        if 'CONTENT_TYPE' in metadict:
            contenttype = metadict['CONTENT_TYPE']
        else:
            raise ContentTypeError('No content_type in request.')

        result = {'type': '', 'charset': ''}

        first = contenttype.split(';')
        result['type'] = first[0].strip()

        for i in range(1, len(first)):
            if '=' in first[i]:
                param = first[i].strip().split('=')
                result[param[0].strip()] = param[1].strip()

        if result['type'].lower() != expectedcontenttype.lower():
            raise ContentTypeError('ContentType is {0}, expected {1}.'.format(result['type'], expectedcontenttype))
        if charsetrequired and result['charset'] in ['', None]:
            raise ContentTypeError('Charset is missing.')

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
            contenttype = self.validContenttype(request.META, JSONRestView.RESTCONTENTTYPE)

            bdy = request.body.decode(contenttype['charset'])
            self.payload = json.loads(bdy)
            retval = HttpResponse()
        except (ContentTypeError, json.decoder.JSONDecodeError) as e:
            retval = HttpResponseBadRequest(
                     self.errorResponse('{0} : {1}'.format(type(e).__name__, e)),
                     content_type=JSONRestView.RESTCONTENTTYPE)

        return retval

    def postfile(self, request, *args, **kwargs):
        '''
        ------------------------------------------------------------
        Base class for POST handler for handling file upload.
        We use multipart/formdata.

        Input: Request.
        Output: HTTP Response of some variety.

        Content-type must equal UPLOADFILECONTENTTYPE.
        ------------------------------------------------------------
        '''

        self.payload = None
        self.payload = {}

        destination = './' + self.tmpfilename()

        try:
            i = 0
            for k,v in request.FILES.items():
                destfn = destination + str(i) + '.csv'
                self.handle_uploaded_file(v, destfn)
                self.payload['file'+str(i)] = v.name + ' moved to ' + destfn

            contenttype = self.validContenttype(request.META, JSONRestView.UPLOADFILECONTENTTYPE, False)
            self.payload['AKA-Bruger'] = request.META['HTTP_X_AKA_BRUGER']
            retval = HttpResponse()
        except (ContentTypeError, json.decoder.JSONDecodeError) as e:
            retval = HttpResponseBadRequest(
                     self.errorResponse('{0} : {1}'.format(e, type(e).__name__)),
                     content_type=JSONRestView.RESTCONTENTTYPE)

        return retval

