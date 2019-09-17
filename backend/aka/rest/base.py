from django.views import View
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.conf import settings
import json
import os
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
    """REST API base class. Untangles request data and stores any files POSTed.

    Data posted in body or in form fields are made available in self.data.

    Files are stored, and their metadata made available in self.files.
    """

    CT1 = 'application/json'        # Accepted content-type.
    CT2 = 'multipart/form-data'     # Accepted content-type.

    def randomstring(self, length=30):
        return ''.join([
            random.choice('abcdefghijklmnopqrstuvwxyz0123456789')
            for i in range(length)
            ])

    def store_uploaded_file(self, f, destinationfilename):
        with open(destinationfilename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    def cleanup(self):
        '''
        Cleanup after file upload.  Removes files from temp folder,
        and deletes the in-memory file list.
        '''

        try:
            for file in self.files:
                os.remove(file['tmpfilename'])
            self.files = []
        except (OSError, AttributeError):
            pass

    def getContenttype(self, metadict):
        '''
        Get contenttype from header.

        :param metadict: A dict, e.g. the request.META dict
        :type metadict: Dictionary
        :returns: dict with at least the two keys type and charset.
                  The values of these may be empty.
        :raises: ContentTypeError
        '''

        if 'CONTENT_TYPE' not in metadict:
            raise ContentTypeError('No content_type in request.')
        else:
            result = {'type': '', 'charset': ''}

            parts = metadict['CONTENT_TYPE'].split(';', 1)
            result['type'] = parts[0].strip().lower()

            for i in range(1, len(parts)):
                if '=' in parts[i]:
                    param = parts[i].strip().split('=')
                    result[param[0].strip()] = param[1].strip()

            return result

    def successResponse(self, msg):
        msg = json.dumps({"status": "Request succeeded",
                          "message": msg})
        return HttpResponse(msg, content_type=JSONRestView.CT1)

    def errorResponse(self, exception):
        '''
        Compose error message from exception.

        :param msg: The error message
        :type msg: String
        :returns: HttpResponseBadRequest  containing the exception.
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
        '''

        return json.loads(request.body.decode(charset))

    def getPost(self, request):
        '''
        Get POST data from the HTTP request.

        :param request: The HttpRequest object
        :type request: HttpRequest
        :returns: Dict containing any data from the POST dict.
        '''
        return request.POST.copy().dict()

    def getFiles(self, request):
        files = []

        for k, v in request.FILES.items():
            destination = settings.MEDIA_URL + self.randomstring() + '.'
            destination += v.name.replace(' ', '_').replace('/', '_s_')
            self.store_uploaded_file(v, destination)
            files.append(
                {'originalname': v.name,
                 'tmpfilename': destination,
                 'filetype': type(v).__name__,
                 'contenttype': v.content_type,
                 'charset': v.charset,
                 'size': v.size})

        return files

    def basepost(self, request, *args, **kwargs):
        '''
        Base method for POST requests.
        We only accept some content-types.

        Stores the data and/or files in self.data and
        self.files, respectively. In self.files, only the file metadata
        is stored.

        Attributes:
            self.data  - dict: Data sent via request.body or request.POST.

            self.files - list: Metadata for any file(s) sent.

        :param request: The request.
        :type request: HttpRequest.
        :returns:  HttpResponse, HttpResponseBadRequest
        :raises: ContentTypeError, json.decoder.JSONDecodeError, IOError
        '''

        self.data = {}
        self.files = []

        try:
            content = self.getContenttype(request.META)

            if content['type'] == JSONRestView.CT1 and \
               content['charset'] in ['', None]:
                raise ContentTypeError('Charset missing.')
            elif content['type'] == JSONRestView.CT1:
                self.data = self.getBody(request,
                                         content['charset'])
            elif content['type'] == JSONRestView.CT2:
                self.data = self.getPost(request)
                # self.files = self.getFiles(request)
                self.files = request.FILES
            else:
                raise ContentTypeError('Content_type incorrect: '
                                       + content['type'])
            retval = self.successResponse("OK")

            logger.info('POST: ' + json.dumps(self.data) + '\n' + json.dumps([{
                'originalname': v.name,
                'filetype': type(v).__name__,
                'contenttype': v.content_type,
                'charset': v.charset,
                'size': v.size
                }
                for k, v in request.FILES.items()
            ]))
        except (ContentTypeError, json.decoder.JSONDecodeError) as e:
            retval = self.errorResponse(e)
            logger.exception(e)

        return retval
