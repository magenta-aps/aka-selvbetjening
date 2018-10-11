from django.views import View
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.conf import settings
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
    # Set a few content types:
    CT1 = 'application/json'
    CT2 = 'multipart/form-data'

    def randomstring(self, length=30):
        return ''.join([
            random.choice('abcdefghijklmnopqrstuvwxyz0123456789')
            for i in range(50)
            ])

    def handle_uploaded_file(self, f, destinationfilename):
        with open(destinationfilename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    def validContenttype(self, metadict, expectedcontenttype,
                         charsetrequired=True):
        '''
        ------------------------------------------------------------
        Validate content_type and charset from Content-Type header string.
        Input: The request.META dict, expected contenttype, and whether
               charset is required or not.
               E.g validContenttype(request.META,
                                    JSONRestView.CT1,
                                    False)

        Output: If all is OK, returns dict with 2 keys guaranteed
                present: 'type' and 'charset'.
                They may have no values, though.
                The key 'type' contains the type/subtype part of
                content_type (i.e. the main element).

                If errors, i.e. missing or incorrect contenttype,
                raises ContentType exceptiom.
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
            raise ContentTypeError('ContentType is {0}, expected {1}.'.
                                   format(result['type'],
                                          expectedcontenttype))
        elif charsetrequired and result['charset'] in ['', None]:
            raise ContentTypeError('Charset is missing.')

        return result

    def errorResponse(self, exception):
        msg = self.errorText('{0} : {1}'.
                             format(type(exception).__name__, exception))

        return HttpResponseBadRequest(msg,
                                      content_type=JSONRestView.CT1)

    def errorText(self, msg):
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

        Content-type must equal CT1.
        charset must have a value.
        ------------------------------------------------------------
        '''

        self.payload = {}

        try:
            # Check size of request?
            contenttype = self.validContenttype(request.META,
                                                JSONRestView.CT1)

            bdy = request.body.decode(contenttype['charset'])
            self.payload = json.loads(bdy)
            retval = HttpResponse()
        except (ContentTypeError, json.decoder.JSONDecodeError) as e:
            retval = self.errorResponse(e)

        return retval

    def postfile(self, request, *args, **kwargs):
        '''
        ------------------------------------------------------------
        Base class for POST handler for handling file upload.
        We use multipart/formdata.
        Django places uploaded files in request.FILES.
        Additional form fields end up in request.POST. The key is the
        field name.

        Input: Request.
        Output: HTTP Response of some variety.

        Content-type must equal CT2.
        ------------------------------------------------------------
        '''

        self.payload = {}

        try:
            self.validContenttype(request.META,
                                  JSONRestView.CT2,
                                  False)

            self.payload['POST'] = request.POST
            self.payload['files'] = []
            for k, v in request.FILES.items():
                destination = settings.MEDIA_URL + self.randomstring() + '.'
                destination += v.name.replace(' ', '_').replace('/', '_s_')
                self.handle_uploaded_file(v, destination)
                self.payload['files'].append(
                    {'originalname': v.name,
                     'tmpfilename': destination,
                     'filetype': type(v).__name__,
                     'contenttype': v.content_type,
                     'charset': v.charset,
                     'size': v.size})

            self.payload['AKA-Bruger'] = request.META['HTTP_X_AKA_BRUGER']
            retval = HttpResponse()
        except (ContentTypeError, json.decoder.JSONDecodeError, IOError) as e:
            retval = self.errorResponse(e)

        return retval
