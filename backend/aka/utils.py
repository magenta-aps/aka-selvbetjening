import base64
import datetime
import json
import logging
import os
from math import floor

from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def datefromstring(datestring):
    '''
    Convert a string of the form YYYY-MM-DD to a datetime object.

    E.g. 20180203 is OK. 2018218 is not OK.

    :param datestring: Date in the form 'YYYY-MM-DD'.
    :type datestring: String
    :returns: datetime object.
    '''

    return datetime.datetime.strptime(datestring, '%Y-%m-%d')


def datetostring(date):
    '''
    Convert a date object to a string of the form YYYY-MM-DD.

    E.g. 20180203 is OK. 2018218 is not OK.

    :param datestring: Date in the form 'YYYY-MM-DD'.
    :type datestring: String
    :returns: datetime object.
    '''

    return datetime.datetime.strftime(date, '%Y-%m-%d')


def get_file_contents(filename):
    with open(filename, "r") as f:
        return f.read()


def get_file_contents_base64(file):
    with file.open('rb') as fp:
        data = fp.read()
        return base64.b64encode(data).decode("ascii")


def getSharedJson(fileName):
    """
    This function generates a json(can be used as a dict)
    from a file shared between the frontend and backend.
    The file must be in a valid json format.

    """
    file_path = os.path.join(settings.SHARED_DIR, fileName)
    with open(file_path, 'r', encoding="utf8") as jsonfile:
        return json.loads(jsonfile.read())


def get_ordereddict_key_index(ordereddict, key):
    for index, k in enumerate(ordereddict):
        if k == key:
            return index
    raise ValueError


def spreadsheet_col_letter(col_index):
    if col_index is None:
        return None
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    length = len(alphabet)
    if col_index >= length:
        return spreadsheet_col_letter(floor(col_index / 26) - 1) + alphabet[col_index % length]
    return alphabet[col_index]


error_definitions = getSharedJson('errors.json')


class ErrorJsonResponse(JsonResponse):

    status_code = 400

    def __init__(self, errors, field_errors, **kwargs):
        data = {
            'errors': errors,
            'fieldErrors': field_errors
        }
        super().__init__(data, **kwargs)

    @staticmethod
    def from_error_dict(error_dict, **kwargs):
        nonfield_errors = []
        field_errors = {}
        for fieldname, errors in error_dict.as_data().items():
            for error in errors:
                translated = [
                    ErrorJsonResponse.translate(error_id)
                    for error_id in error.messages
                ]
                if fieldname == NON_FIELD_ERRORS:
                    nonfield_errors += translated
                else:
                    field_errors[fieldname] = translated
        return ErrorJsonResponse(nonfield_errors, field_errors, **kwargs)

    @staticmethod
    def from_error_id(error_id, fieldname=None, **kwargs):
        nonfield_errors = []
        field_errors = {}
        translated = ErrorJsonResponse.translate(error_id)
        if fieldname is None or fieldname == NON_FIELD_ERRORS:
            nonfield_errors.append(translated)
        else:
            field_errors[fieldname] = translated
        return ErrorJsonResponse(nonfield_errors, field_errors, **kwargs)

    @staticmethod
    def from_exception(exception, **kwargs):
        return ErrorJsonResponse.from_error_id(
            f"{type(exception).__name__}: {exception}",
            **kwargs
        )

    @staticmethod
    def translate(error_id):
        if type(error_id) == list:
            return [ErrorJsonResponse.translate(i) for i in error_id]
        if error_id not in error_definitions:
            logger.error("errorId: \"" + error_id + "\" not found")
            return {"da": error_id, "kl": error_id}
        else:
            return error_definitions[error_id]

    @staticmethod
    def invalid_month():
        return ErrorJsonResponse.from_error_id("invalid_month")

    @staticmethod
    def future_month():
        return ErrorJsonResponse.from_error_id("future_month")


class AccessDeniedJsonResponse(ErrorJsonResponse):
    status_code = 403

    def __init__(self, **kwargs):
        super(AccessDeniedJsonResponse, self).__init__(['Access denied'], [], **kwargs)


def format_filesize(bytes, digits=1, SI=True):
    stepsize = 1000 if SI else 1024
    now = 1
    next = stepsize
    for step in ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']:
        if bytes < next:
            if step:
                return ("{0:.%df} %s%sB" % (digits, step, '' if SI else 'i')).format(bytes / now)
            return "%d B" % bytes
        now = next
        next *= stepsize

def list_lstrip(l, strip=None):
    l = l.copy()  # Work on a copy of the list
    while l and l[0] == strip:
        l = l[1:]
    return l

def list_rstrip(l, strip=None):
    l = l.copy()  # Work on a copy of the list
    while l and l[-1] == strip:
        l = l[:-1]
    return l

def list_strip(l, strip=None):
    return list_rstrip(list_lstrip(l, strip), strip)
