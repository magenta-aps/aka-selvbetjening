import datetime
import base64
import json
import os

from django.conf import settings


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
