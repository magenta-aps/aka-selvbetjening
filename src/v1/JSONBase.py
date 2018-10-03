from django.views import View
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
import json
import sys

class JSONRestView(View):

    def getContenttype(self, typestring):
        '''
        ------------------------------------------------------------
        Get content_type.
        Input: The value of the 'CONTENT_TYPE' key in request.META.
               Expects something like this: 'type/subtype [; charset=xyz]'
        Output: Dict with 2 keys guaranteed present: 'type' and 'charset'. They may have no values, though.
                The key 'type' contains the type/subtype part of content_type (i.e. the main element).
        ------------------------------------------------------------
        '''
        result = { 'type' : '', 'charset' : '' }

        first = typestring.split(';')

        for i in range(1,len(first)):
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
        Output: String that is a serialised JSON structure, with the error message incorporated.
        ------------------------------------------------------------
        '''
        return json.dumps({ "status" : "Request failed.", "message":msg })


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
        CONTENT_TYPE = 'application/json'

        self.payload = None

        try:
            # Check size of request?
            if 'CONTENT_TYPE' in request.META:
                contenttype = self.getContenttype(request.META['CONTENT_TYPE'])
            else:
                raise Exception('No content_type in request.')

            if contenttype['type'].lower() != CONTENT_TYPE.lower():
                raise Exception('Contenttype must be ' + CONTENT_TYPE + ', not ' + contenttype['type'])
            elif contenttype['charset'] is None or contenttype['charset'] == '':
                raise Exception('Charset is missing.')

            bdy = request.body.decode(contenttype['charset'])
            self.payload = json.loads(bdy)
            retval = HttpResponse()
        except json.decoder.JSONDecodeError as err:
            retval = HttpResponseBadRequest(self.errorResponse('JSONDecodeError. {0}'.format(err)))
        except:
            retval = HttpResponseBadRequest(self.errorResponse(str(sys.exc_info()[1])))

        return retval
