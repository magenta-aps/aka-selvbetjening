from akasite.rest.base import JSONRestView
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
import json
import logging
import re



logger = logging.getLogger(__name__)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class InkassoSag(JSONRestView):
    def get(self, request, *args, **kwargs):
        dummyresponse = {"serversays": "Hello. You said InkassoSag/GET"}

        return HttpResponse(json.dumps(dummyresponse),
                            content_type=JSONRestView.RESTCONTENTTYPE)

    def post(self, request, *args, **kwargs):
        baseresponse = super().post(request, args, kwargs)


        if baseresponse.status_code == 200:

            logger.info(self.payload)
            validateFordringsgrupper(self.payload)

            return HttpResponse(200)
        else:
            return baseresponse

def validateFordringsgrupper(reqJson):
    fordringsJson = getFordringsgrupper()
    try:
        fordringsgruppe = getOnlyElement(fordringsJson, reqJson['fordringsgruppe'])
    except Exception as e:
        return {
                    'status': False,
                    'field': 'fordringsgruppe',
                    'msg': str.format(e,'fordringsgruppe')
               }
    try:
        fordringstype = getOnlyElement(fordringsgruppe['sub_groups'], reqJson['fordringstype'])

    except Exception as e:
        return {
                    'status': False,
                    'field': 'fordringstype',
                    'msg': str.format(e,'fordringstype')
               }

    return {'status': True}





def getOnlyElement(l, fordring):
    fordringsList = [x for x in l if x['id']==fordring]
    if len(fordringsList ) < 1:
        logger.error("The following list:\n"+l+"\n was expected to have 1 "+
                     "element with the following id: "+fordring+
                     ", but none was found.\n"+
                     "The error might be a user error, if a custom REST-client was used")
        raise Exception("Error {0} not found")

    elif len(fordringsList ) > 1:
        logger.error("The following list:\n"+l+"\n was only expected to have 1 "+
                     "element with the following id: "+fordring+
                     ", but multiple elements were found")
        raise Exception("Server Error, multiple {0} fields found")

    else:
        return fordringsList[0]


def quoteJson(unquotedJson):
    temp1 = unquotedJson.replace(r'id:', r'"id":')
    temp2 = temp1.replace(r'value:', r'"value":')
    temp3 = temp2.replace(r'sub_groups:', r'"sub_groups":')
    return temp3

def getFordringsgrupper():
    """

    """
    with open('../shared/fordringsgruppe.json','r') as jsonfile:
        validjson = quoteJson(jsonfile.read())
        return json.loads(validjson)



