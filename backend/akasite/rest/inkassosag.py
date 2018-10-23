from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

import json
import logging
import re

# Internal tools
from akasite.rest.base import JSONRestView
from akasite.rest.validation import JsonValidator

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
        baseresponse = super().postfile(request)

        if baseresponse.status_code == 200:

            logger.info(self.payload)
            validation1 = validateInkassoJson(self.payload['POST'])
            if validation1 == []:
                validationStatus = validateFordringsgrupper(self.payload['POST'])
            else:
                validationStatus = validation1

            return HttpResponse(json.dumps(validationStatus),
                                content_type=JSONRestView.CT1)
        else:
            return baseresponse


def validateInkassoJson(reqJson):
    jsonSchema = {
            'type': 'object',
            'properties': {
                'fordringshaver':   {'type': 'string'},
                'debitor':          {'type': 'string'},
                'fordringshaver2':  {'type': 'string'},
                'fordringsgruppe':  {'type': 'integer'},
                'fordringstype':    {'type': 'integer'}
                },
            'required': ['fordringshaver',
                         'debitor',
                         'fordringshaver2',
                         'fordringsgruppe',
                         'fordringstype']
            }

    return JsonValidator(jsonSchema).validate(reqJson)


def validateFordringsgrupper(reqJson):
    try:
        fordringsJson = getSharedJson('fordringsgruppe.json')
        fordringsgruppe = getOnlyElement(fordringsJson,
                                         reqJson['fordringsgruppe'])
        if fordringsgruppe['status']:
            fordringstype = getOnlyElement(fordringsgruppe['elem']['sub_groups'],
                                           reqJson['fordringstype'])
            if fordringstype['status']:
                return {'status': True}
            else:
                return fordringstype
        else:
            return fordringsgruppe
    except Exception as e:
        logger.warning("Invalid JSON recieved:"+str(reqJson)+"\n\nException: "+e)
        return {
                    'status': False,
                    'msg': 'fordringsgruppe or fordringstype missing or NaN'
               }


def getOnlyElement(l, fordring):
    fordringsList = [x for x in l if x['id'] == fordring]
    if len(fordringsList) < 1:
        logger.error("The following list:\n" + str(l) + "\n was expected to " +
                     "have 1 element with the following id: " + fordring +
                     ", but none was found.\n" +
                     "The error might be a user error, if a custom " +
                     "REST-client was used")
        return {
                    'status': False,
                    'field': 'fordringsgruppe',
                    'msg': str.format(str(e), 'fordringsgruppe')
               }

    elif len(fordringsList) > 1:
        logger.error("The following list:\n" + str(l) + "\n was only " +
                     "expected to have 1 element with the following id: " +
                     str(fordring) + ", but multiple elements were found")
        return {
                    'status': False,
                    'field': 'fordringstype',
                    'msg': str.format(str(e), 'fordringstype')
               }
    else:
        return {'status': True, 'elem': fordringsList[0]}


def getSharedJson(fileName):
    """
    This function generates a json(can be used as a dict)
    from a file shared between the frontend and backend.
    The file must be in a valid json format.

    """
    with open('../shared/'+fileName, 'r') as jsonfile:
        return json.loads(jsonfile.read())
