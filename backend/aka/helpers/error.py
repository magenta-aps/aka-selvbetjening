import logging

from aka.helpers.sharedfiles import getSharedJson
from django.core.exceptions import NON_FIELD_ERRORS
from django.http import JsonResponse

error_definitions = getSharedJson('errors.json')
logger = logging.getLogger(__name__)


class ErrorJsonResponse(JsonResponse):

    status_code = 400

    def __init__(self, error_dict, **kwargs):
        data = {
            'errors': [],
            'fieldErrors': {}
        }
        for fieldname, errors in error_dict.as_data().items():
            for error in errors:
                error_ids = error.messages
                if fieldname == NON_FIELD_ERRORS:
                    data['errors'] += self.translate(error_ids)
                else:
                    data['fieldErrors'][fieldname] = self.translate(error_ids)
        super().__init__(data, **kwargs)

    def translate(self, error_id):
        if type(error_id) == list:
            return [self.translate(i) for i in error_id]
        if error_id not in error_definitions:
            logger.error("errorId: \"" + error_id + "\" not found")
            return {"da": error_id, "kl": error_id}
        else:
            return error_definitions[error_id]
