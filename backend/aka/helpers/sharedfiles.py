import json
import logging
import os

from django.conf import settings

logger = logging.getLogger(__name__)


def getSharedJson(fileName):
    """
    This function generates a json(can be used as a dict)
    from a file shared between the frontend and backend.
    The file must be in a valid json format.

    """
    file_path = os.path.join(settings.SHARED_DIR, fileName)
    with open(file_path, 'r', encoding="utf8") as jsonfile:
        return json.loads(jsonfile.read())
