import json
import logging

logger = logging.getLogger(__name__)


def getSharedJson(fileName):
    """
    This function generates a json(can be used as a dict)
    from a file shared between the frontend and backend.
    The file must be in a valid json format.

    """
    with open('../shared/'+fileName, 'r') as jsonfile:
        return json.loads(jsonfile.read())
