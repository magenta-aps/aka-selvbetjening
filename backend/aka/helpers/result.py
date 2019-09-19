from django.http import HttpResponse

from aka.rest.base import JSONRestView
from aka.helpers.sharedfiles import getSharedJson

import json
import logging

logger = logging.getLogger(__name__)

######################
#   Result Objects   #
######################

errorJson = getSharedJson('errors.json')
__ERR_MSG = 'Result is an Abstract class, use either Success or Error instead'


class __Result():
    '''This Abstract class represents a validation Result

    **warning**: DO NOT USE DIRECTLY, THIS IS AN ABSTRACT CLASS

    The methods in these classes does not mutate the Object, they return a
    new object.
    This is sort of inefficient, but it should never be used in a degree,
    where it would be a problem.
    The reason is that mutating the object to always be correct after a method
    call would be complicated, and most likely produce bugs, and since method
    chaining works very well with theese methods, they would still need to
    return something.

    The intent of this class, is to free the programmer from thinking about 
    - or checking - whether or not a validation succeeded or failed, 
    until the very end, but still making sure errors are not silently ignored.

    '''
    def append(self, validation):
        '''Appends Results

        Appends 2 Successes/Errors, into a new Success/Error

        This is kind of like a logical *AND* on the result.status
        If both are Successes, its a Success
        If only one is an Error, that Error is returned
        If both are Errors, the errormessages are appended, and returned
        as a new single Error object, with multiple errormessages


        :param validation: The Success/Error to be appended
        :type validation: Success, Error

        '''
        raise NotImplementedError(__ERR_MSG)

    def map(self, f):
        '''Transform the :code:`value` according to :code:`f`

        :param f: Function to transform the value
        :type f: Function(value -> value')
        '''
        raise NotImplementedError(__ERR_MSG)

    def either(self, validation, error):
        '''Return a Success if either this or the parameter is a Success

        **warning**: using :code:`andThen` after :code:`either` may not work
        as intended! since you will not know which of the Results will be used

        This is kind of like a logical *OR* on the result.status

        :param validation: The Success/Error to return if this is an error
        :type validation: Success, Error
        :param error: The error to be returned if both are errors
        :type error: Error
        '''
        raise NotImplementedError(__ERR_MSG)

    def andThen(self, f):
        '''Run the function on successfull result

        Run the function :code:`f` with the value of the Success.
        This method is supposed to be used, when the next validation depends
        on a value generated by the current validation.

        Eg: getting the first element of a list, andThen validating that
            element, the validation of the element cannot occur, if it was an
            empty list, as there would be no element.

        **warning**: :code:`f` should return a new Success/Error

        **warning**: :code:`andThen` should usually be applied directly
        on a Result, not after an :code:`append` or :code:`either` or
        some other method, as it will usually not work as intended.

        :param f: The function to be executed
        :type f: Function(value -> Success/Error)
        '''
        raise NotImplementedError(__ERR_MSG)

    def toHttpResponse(self):
        '''Return a HttpRespons representation of the result

        '''
        raise NotImplementedError(__ERR_MSG)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return self.__dict__ != other.__dict__


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
        return Success(f(self.value))

    def either(self, validation, error):
        return self

    def andThen(self, f):
        return f(self.value)

    def toHttpResponse(self):
        return HttpResponse(json.dumps(self.value), status=200,
                            content_type=JSONRestView.CT1)

    def __str__(self):
        d = {"status": self.status, "errors": self.errors,
                                    "fieldErrors": self.fieldErrors}
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
            errMsg = {"da": errorId, "kl": errorId}
        else:
            errMsg = errorJson[errorId]

        if field is None:
            self.errors = [errMsg]
            self.fieldErrors = dict()
        else:
            self.fieldErrors = dict({field: errMsg})
            self.errors = []

    def append(self, validation):
        newErr = self
        newErr.errors.extend(validation.errors)
        newErr.fieldErrors.update(validation.fieldErrors)
        return newErr

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
        d = {"errors": self.errors, "fieldErrors": self.fieldErrors}
        return HttpResponse(json.dumps(d), status=400,
                            content_type=JSONRestView.CT1)

    def __str__(self):
        d = {"status": self.status, "errors": self.errors,
                                    "fieldErrors": self.fieldErrors}
        return json.dumps(d)

    @staticmethod
    def invalid_month():
        return Error('invalid_month')
