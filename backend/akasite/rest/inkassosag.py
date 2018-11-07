from django.http import HttpResponse

import json
import logging
import re

# Internal tools
from akasite.rest.base import JSONRestView
from akasite.rest import validation
from akasite.rest.validation import Error, Success
from akasite.helpers.sharedfiles import getSharedJson

logger = logging.getLogger(__name__)


class InkassoSag(JSONRestView):
    '''This class handles the REST interface at /inkassosag

    It implements a POST endpoint. It should not be called directly,
    but is instead called by Django's url handler.

    '''

    def post(self, request, *args, **kwargs):
        '''
        Method for POST handler at /inkassosag

        :param request: The request.
        :type request: HttpRequest.
        :returns: HttpResponse, HttpResponseBadRequest

        '''
        baseresponse = super().post(request)

        if baseresponse.status_code == 200:

            logger.debug(self.data)
            return (validateInkassoJson(self.data)
                    .andThen(validateFordringsgrupper)
                    .toHttpResponse()
                    )
        else:
            return baseresponse


jsonSchema = {
        'type': 'object',
        'properties': {
            'fordringshaver':   {'type': 'string'},
            'debitor':          {'type': 'string'},
            'fordringshaver2':  {'type': 'string'},
            'fordringsgruppe':  {
                'type': 'string',
                'pattern': '[0-9]+'
                },
            'fordringstype':    {'type': 'string'}
            },
        'required': ['fordringshaver',
                     'debitor',
                     'fordringsgruppe',
                     'fordringstype']
        }


def validateInkassoJson(reqJson):
    '''Validate a dict data-structure for the /inkassosag endpoint

    :param reqJson: The Json to be validated
    :type reqJson: Dict
    :returns: Error, Success

    '''
    __REQUIRED_FIELDS = ['fordringshaver',
                         'debitor',
                         'fordringsgruppe',
                         'fordringstype']
    return validation.validateRequired(__REQUIRED_FIELDS, reqJson)


def validateFordringsgrupper(reqJson):
    '''Validate that a given request's fordrings-gruppe and type is valid

    :param reqJson: The Json to be validated
    :type reqJson: Dict
    :returns: Error, Success

    '''
    try:
        fordringJson = getSharedJson('fordringsgruppe.json')
        return (getOnlyElement(fordringJson, reqJson['fordringsgruppe'],
                               'fordringsgruppe')
                .andThen(lambda e: getOnlyElement(e['sub_groups'],
                                                  reqJson['fordringstype'],
                                                  'fordringstype'))
                )
    except Exception as e:
        logger.warning("Invalid JSON recieved:" + str(reqJson)
                       + "\n\nException: " + str(e))
        return Error('fordringsgruppe_or_type_problem')


def getOnlyElement(l, fid, fordringsName):
    '''Get 1 element, if only one exists, otherwise an Error is returned

    Finds exactly one element(Dict), with a field `id` which has the same
    value as `fid`, if no element matches, or multiple elements matches
    an Error is instead returned.
    Because it can return an error, it returns a Success(Dict) instead
    of just the Dict with the given element.
    An easy way to use the Dict, upon success is using Success.andThen.
    See :func:`~akasite.rest.validation.Success.andThen`

    :param l: The list to look for the element in
    :type l: List
    :param fid: The id to look for
    :type fid: String
    :param fordringsName: The name of the fordring(used for the errors)
    :type fordringsName: String
    :returns: Success(Dict), Error

    '''
    fordringsList = [x for x in l if x['id'] == fid]
    if len(fordringsList) < 1:
        logger.warning("The following list:\n" + str(l) + "\n was expected to "
                       + "have 1 element with the following id: " + fid
                       + ", but none was found.\n"
                       + "The error might be a user error, if a custom "
                       + "REST-client was used")
        return Error(fordringsName + '_not_found', fordringsName)

    elif len(fordringsList) > 1:
        logger.error("The following list:\n" + str(l) + "\n was only "
                     + "expected to have 1 element with the following id: "
                     + str(fid) + ", but multiple elements were found")
        return Error('multiple_' + fordringsName + '_found', fordringsName)
    else:
        return Success(fordringsList[0])
