from django.http import HttpResponse

from akasite.rest.base import JSONRestView
from akasite.helpers.sharedfiles import getSharedJson

import json
import logging
import re

logger = logging.getLogger(__name__)

######################
#   Result Objects   #
######################

errorJson = getSharedJson('errors.json')

class __Result():
    '''This Abstract class represents a validation Result

    **warning**: DO NOT USE DIRECTLY, THIS IS AN ABSTRACT CLASS

    '''
    def append(self, validation):
        '''Appends Results

        Appends 2 Successes/Errors, into a new Success/Error

        :param validation: The Success/Error to be appended
        :type validation: Success, Error

        '''
        raise Exception('Result is an Abstract class, use either Success or Error instead')

    def map(self, f):
        '''Transform the :code:`value` according to :code:`f`

        :param f: Function to transform the value
        :type f: Function(value -> value')
        '''
        raise Exception('Result is an Abstract class, use either Success or Error instead')

    def either(self, validation, error):
        '''Return a Success if either this or the parameter is a Success

        **warning**: using :code:`andThen` after :code:`either` may not work
        as intended! since you will not know which of the Results will be used

        :param validation: The Success/Error to return if this is an error
        :type validation: Success, Error
        :param error: The error to be returned if both are errors
        :type error: Error
        '''
        raise Exception('Result is an Abstract class, use either Success or Error instead')

    def andThen(self, f):
        '''Run the function on successfull result

        Run the function :code:`f` with the value of the Success.

        **warning**: :code:`f` should return a new Success/Error

        **warning**: :code:`andThen` should usually be applied directly
        on a Result, not after an :code:`append` or :code:`either` or
        some other method, as it will usually not work as intended.

        :param f: The function to be executed
        :type f: Function(value -> Success/Error)
        '''
        raise Exception('Result is an Abstract class, use either Success or Error instead')

    def toHttpResponse(self):
        '''Return a HttpRespons representation of the result

        '''
        raise Exception('Result is an Abstract class, use either Success or Error instead')

class Success(__Result):
    '''This class represents a validation result that succeeded

    A Success initialization accepts and parameter, which is the
    object a function would return when everything is successfull.

    '''
    def __init__(self, value):
        '''Initialize a Success

        :param value: the value returned from a Successfull computation
        :type value: Object

        '''
        self.status = True
        self.errors = []
        self.fieldErrors = dict()
        self.value = value

    def append(self, validation):
        return validation

    def map(self, f):
        self.value = f(value)
        return self

    def either(self, validation, error):
        return self

    def andThen(self, f):
        return f(self.value)

    def toHttpResponse(self):
        d = { "errors": self.errors, "fieldErrors": self.fieldErrors}
        return HttpResponse(json.dumps(d),status=200,content_type=JSONRestView.CT1)

    def __str__(self):
        d = { "status": self.status,"errors": self.errors, "fieldErrors": self.fieldErrors}
        return json.dumps(d)


class Error(__Result):
    '''This class represents a validation result that failed

    The errorId is a key in the `shared/errors.json` file, when making a new
    error message, you MUST write it in `shared/errors.json` file, to ensure
    proper translation.


    '''
    def __init__(self, errorId, field=None):
        '''Initializes an Error

        :param errorId: Key in shared/errors.json
        :type errorId: String
        :param field: Optional field name where the error originated
        :type field: String

        '''
        self.status = False

        if errorId not in errorJson:
            logger.error("errorId: \"" + errorId + "\" not found")
            errMsg = { "da": errorId, "kl": errorId }
        else:
            errMsg = errorJson[errorId]

        if field==None:
            self.errors = [errMsg]
            self.fieldErrors = dict()
        else:
            self.fieldErrors = dict(field=errMsg)
            self.errors = []

    def append(self, validation):
        self.errors = self.errors + validation.errors
        self.fieldErrors.update(validation.fieldErrors)
        return self

    def map(self, f):
        return self

    def either(self, validation, error):
        if validation.status:
            return validation
        else:
            return error

    def andThen(self, f):
        return self

    def toHttpResponse(self):
        d = { "errors": self.errors, "fieldErrors": self.fieldErrors}
        return HttpResponse(json.dumps(d),status=400,content_type=JSONRestView.CT1)

    def __str__(self):
        d = { "status": self.status,"errors": self.errors, "fieldErrors": self.fieldErrors}
        return json.dumps(d)

####################
#    Validators    #
####################

# If you do not know what to return on Success, return the input which
# would likely be used for further validation
# eg. validateRequired() returns the requestDict, as it is usually used
# for the next step in the validation

def validateRequired(requiredFields, requestDict):
    result = Success(requestDict)
    for field in requiredFields:
        if field in requestDict.keys():
            continue
        else:
            result = result.append(Error('required_field',field))

    return result
