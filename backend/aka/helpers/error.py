import logging

from django.core.exceptions import NON_FIELD_ERRORS
from django.http import JsonResponse

from .utils import getSharedJson

error_definitions = getSharedJson('errors.json')
logger = logging.getLogger(__name__)


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
        super(AccessDeniedJsonResponse, self).__init__(None, None, **kwargs)
