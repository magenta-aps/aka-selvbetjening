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
            for i in range(length)
            ])

    def store_uploaded_file(self, f, destinationfilename):
        with open(destinationfilename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    def getContenttype(self, metadict):
        '''
        Get contenttype, or raise exception if not found.

        :param metadict: A dict, e.g. the request.META dict
        :type metadict: Dictionary
        :returns: dict with at least the two keys type and charset.
                  The values of these may be empty.
        '''

        if 'CONTENT_TYPE' not in metadict:
            raise ContentTypeError('No content_type in request.')
        else:
            result = {'type': '', 'charset': ''}

            first = metadict['CONTENT_TYPE'].split(';')
            result['type'] = first[0].strip().lower()

            for i in range(1, len(first)):
                if '=' in first[i]:
                    param = first[i].strip().split('=')
                    result[param[0].strip()] = param[1].strip()

            return result

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
        :returns: A copy of the POST dict.
        '''

        return request.POST.copy()

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

    def post(self, request, *args, **kwargs):
        '''
        Base method for POST requests.
        We currently only accept
        a) application/json and
        b) multipartform-data as content-type.
        If a), data is expected to arrive as serialised JSON in body.
        If b), data is in request.POST, and files are in request.FILES.

        In any case, we store the data and/or files in self.data and
        self.files, respectively. In self.files, only the file metadata
        is stored.

        :param request: The request.
        :type request: HttpRequest.
        :returns:  HttpResponse, HttpResponseBadRequest
        :raises: ContentTypeError, json.decoder.JSONDecodeError, IOError
        '''

        self.data = {}
        self.files = []

        try:
            contenttype = self.getContenttype(request.META)

            if contenttype['type'] == JSONRestView.CT1 and \
               contenttype['charset'] in ['', None]:
                raise ContentTypeError('Charset missing.')
            elif contenttype['type'] == JSONRestView.CT1:
                self.data = self.getBody(request,
                                         contenttype['charset'])
            elif contenttype['type'] == JSONRestView.CT2:
                self.data = self.getPost(request)
                self.files = self.getFiles(request)
            else:
                raise ContentTypeError('Content_type incorrect: ' +
                                       contenttype['type'])
            retval = HttpResponse()

            logger.info('POST: ' + json.dumps(self.data) + '\n' +
                        json.dumps(self.files))
        except (ContentTypeError, json.decoder.JSONDecodeError) as e:
            retval = self.errorResponse(e)
            logger.exception(e)

        return retval
