import base64
import datetime
import json
import logging
import os
from math import floor

from django.conf import settings

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

def dummy_management_form(name, total_forms=1, initial_forms=1, min_forms=1, max_forms=1000):
    return {
        "%s-TOTAL_FORMS" % name: total_forms,
        "%s-INITIAL_FORMS" % name: initial_forms,
        "%s-MIN_NUM_FORMS" % name: min_forms,
        "%s-MAX_NUM_FORMS" % name: max_forms,
    }
