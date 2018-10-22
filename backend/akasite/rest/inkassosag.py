from akasite.rest.base import JSONRestView
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
import json
import logging
import re



logger = logging.getLogger(__name__)

class FordringsException(Exception):
    def __init__(self, message):
        super(FordringsException, self).__init__(message)


class InkassoSag(JSONRestView):
    def get(self, request, *args, **kwargs):
        dummyresponse = {"serversays": "Hello. You said InkassoSag/GET"}

        return HttpResponse(json.dumps(dummyresponse),
                            content_type=JSONRestView.CT1)

    def post(self, request, *args, **kwargs):
        baseresponse = super().post(request, args, kwargs)


        if baseresponse.status_code == 200:

            logger.info(self.payload)
            validationStatus = validateFordringsgrupper(self.payload)


            return HttpResponse(str(validationStatus))
        else:
            return baseresponse

def validateFordringsgrupper(reqJson):
    try:
        fordringsJson = getSharedJson('fordringsgruppe.json')
        try:
            fordringsgruppe = getOnlyElement(fordringsJson, reqJson['fordringsgruppe'])
        except FordringsException as e:
            return {
                        'status': False,
                        'field': 'fordringsgruppe',
                        'msg': str.format(str(e),'fordringsgruppe')
                   }
        try:
            fordringstype = getOnlyElement(fordringsgruppe['sub_groups'], reqJson['fordringstype'])

        except FordringsException as e:
            return {
                        'status': False,
                        'field': 'fordringstype',
                        'msg': str.format(str(e),'fordringstype')
                   }

        return {'status': True}
    except Exception as e:
        logger.warning("Invalid JSON recieved:"+str(reqJson)+"\n\nException: "+e)
        return {
                    'status': False,
                    'msg': 'fordringsgruppe or fordringstype missing or not a number'
               }





def getOnlyElement(l, fordring):
    fordringsList = [x for x in l if x['id']==fordring]
    if len(fordringsList ) < 1:
        logger.error("The following list:\n"+str(l)+"\n was expected to have 1 "+
                     "element with the following id: "+fordring+
                     ", but none was found.\n"+
                     "The error might be a user error, if a custom REST-client was used")
        raise FordringsException("Error {0} not found")

    elif len(fordringsList ) > 1:
        logger.error("The following list:\n"+str(l)+"\n was only expected to have 1 "+
                     "element with the following id: "+str(fordring)+
                     ", but multiple elements were found")
        raise FordringsException("Server Error, multiple {0} fields found")

    else:
        return fordringsList[0]


def getSharedJson(fileName):
    """
    This function generates a json(can be used as a dict)
    from a file shared between the frontend and backend.
    The file must be in a valid json format.

    """
    with open('../shared/'+fileName,'r') as jsonfile:
        return json.loads(jsonfile.read())


