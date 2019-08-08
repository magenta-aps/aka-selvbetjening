import logging

# Internal tools
from aka.rest.base import JSONRestView
from aka.helpers import validation
from aka.helpers.result import Error, Success
from aka.helpers.sharedfiles import getSharedJson

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
        baseresponse = super().basepost(request)

        if baseresponse.status_code == 200:

            logger.debug(self.data)
            # For information on "andThen" see documentation for Result
            return (validateInkassoJson(self.data)
                    .andThen(validatePeriodeStartAndEnd)
                    .andThen(validateFordringsgrupper)
                    .toHttpResponse()
                    )
        else:
            return baseresponse


def validateInkassoJson(reqJson):
    '''Validate a dict data-structure for the /inkassosag endpoint

    :param reqJson: The Json to be validated
    :type reqJson: Dict
    :returns: Error, Success

    '''
    __REQUIRED_FIELDS = ['fordringshaver',
                         'debitor',
                         'fordringsgruppe',
                         'fordringstype',
                         'periodestart',
                         'periodeslut']
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
    See :func:`~aka.helpers.result.Success.andThen`

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


def validatePeriodeStartAndEnd(reqJson):
    ''' Validate that starting of period precedes the end of a given period

    :param reqJson: The json from the http request
    :type reqJson: Dict
    '''
    # TODO Are these fields guarenteed to be here?
    if reqJson['periodestart'] <= reqJson['periodeslut']:
        return Success(reqJson)
    else:
        return Error('start_date_before_end_date', 'periodeslut')
