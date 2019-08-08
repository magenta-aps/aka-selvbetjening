from aka.helpers.result import Success, Error

import logging

logger = logging.getLogger(__name__)

####################
#    Validators    #
####################

# If you do not know what to return on Success, return the input which
# would likely be used for further validation
# eg. validateRequired() returns the requestDict, as it is usually used
# for the next step in the validation

# There are more validators in the different rest-views, that are specific for 
# these views.


def validateRequired(requiredFields, requestDict):
    ''' Validate required fields are present

    :param requiredFields: A list of required fields
    :type requiredFields: List of Strings
    :param requestDict: The Dict from the frontend
    :type requestDict: Dict
    '''
    result = Success(requestDict)
    for field in requiredFields:
        if field in requestDict.keys():
            continue
        else:
            result = result.append(Error('required_field', field))

    return result
