from django.views import View
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.conf import settings
import json
import random
import logging

logger = logging.getLogger(__name__)
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

    def getContenttype(self, headerstring):
        result = {'type': '', 'charset': ''}

        first = headerstring.split(';')
        result['type'] = first[0].strip()

        for i in range(1, len(first)):
            if '=' in first[i]:
                param = first[i].strip().split('=')
                result[param[0].strip()] = param[1].strip()

        return result

    def validContenttype(self, metadict, expectedcontenttype,
                         charsetrequired=True):
        '''
        Validate content_type and charset from Content-Type header string.

        :param metadict: The request.META dict
        :type metadict: Dictionary
        :param expectedcontenttype: Expected contenttype
        :type expectedcontenttype: String
        :param charsetrequired: Charset required or not
        :type charsetrequired: Boolean
        :returns A dict with 2 keys guaranteed
                present: 'type' and 'charset'.
                They may have no values, though.
                The key 'type' contains the type/subtype part of
                content_type (i.e. the main element).
        :raises: ContentTypeError
        ------------------------------------------------------------
        '''
        if 'CONTENT_TYPE' in metadict:
            result = self.getContenttype(metadict['CONTENT_TYPE'])
        else:
            raise ContentTypeError('No content_type in request.')

        if result['type'].lower() != expectedcontenttype.lower():
            raise ContentTypeError('ContentType is {0}, expected {1}.'.
                                   format(result['type'],
                                          expectedcontenttype))
        elif charsetrequired and result['charset'] in ['', None]:
            raise ContentTypeError('Charset is missing.')

        return result

    def errorResponse(self, exception):
        '''
        Compose error message from exception.

        :param msg: The error message
        :type msg: String
        :returns: HttpResponseBadRequest  containing the exception.
        ------------------------------------------------------------
        '''
        msg = self.errorText('{0} : {1}'.
                             format(type(exception).__name__, exception))

        return HttpResponseBadRequest(msg,
                                      content_type=JSONRestView.CT1)

    def errorText(self, msg):
        '''
        Create error text as serialised JSON.

        :param msg: The error message
        :type msg: String
        :returns: String that is a serialised JSON structure, with the
                  error message incorporated.
        ------------------------------------------------------------
        '''
        return json.dumps({"status": "Request failed.", "message": msg})

    def getBody(self, request, charset):
        '''
        Get body of HTTP request.

        :param request: The HttpRequest object
        :type request: HttpRequest
        :param charset: The character set of the request
        :type charset: String
        :returns: The request body converted to JSON.
        ------------------------------------------------------------
        '''
        return json.loads(request.body.decode(charset))

    def getPost(self, request):
        '''
        Get POST data from the HTTP request.

        :param request: The HttpRequest object
        :type request: HttpRequest
        :returns: A copy of the POST dict.
        ------------------------------------------------------------
        '''
        return request.POST.copy().dict()

    def post(self, request, *args, **kwargs):
        '''
        Base method for POST handler without file upload.
        For basic JSON POST requests, payload is in request body.

        :param request: The request.
        :type request: HttpRequest.
        :returns:  HttpResponse, HttpResponseBadRequest
        :raises: ContentTypeError, json.decoder.JSONDecodeError, IOError
        '''

        self.payload = {}

        try:
            # Check size of request?
            contenttype = self.validContenttype(request.META,
                                                JSONRestView.CT1)

            self.payload = self.getBody(request,
                                        contenttype['charset'])

            retval = HttpResponse()
            logger.info(json.dumps(self.payload))
        except (ContentTypeError, json.decoder.JSONDecodeError) as e:
            retval = self.errorResponse(e)
            logger.exception(e)

        return retval

    def postfile(self, request, *args, **kwargs):
        '''
        Base method for POST handler for file upload.
        We use multipart/formdata.
        Django places uploaded files in request.FILES.
        Additional form fields end up in request.POST.
        Moves any uploaded files in the directory settings.MEDIA_URL.
        Stores file metadata in self.payload['file'].
        Stores form fields in self.payload['POST'].

        :param request: The request.
        :type request: HttpRequest.
        :returns:  HttpResponse, HttpResponseBadRequest
        :raises: ContentTypeError, json.decoder.JSONDecodeError, IOError
        '''

        self.payload = {}

        try:
            self.validContenttype(request.META,
                                  JSONRestView.CT2,
                                  False)

            self.payload['POST'] = self.getPost(request)
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

            self.authuser = request.META['HTTP_X_AKA_BRUGER']
            retval = HttpResponse()
            logger.info('Uploaded files: ' +
                                             str(len(self.payload['files'])))
        except (ContentTypeError, json.decoder.JSONDecodeError, IOError) as e:
            retval = self.errorResponse(e)
            logger.exception(e)

        return retval
