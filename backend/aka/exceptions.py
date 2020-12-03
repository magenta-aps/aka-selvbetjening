from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class AkaException(Exception):

    title = "common.error.generic"

    def __init__(self, error_code, **params):
        self.error_code = error_code
        self.params = params

    @property
    def message(self):
        try:
            return _(self.error_code).format(**self.params)
        except KeyError as e:
            return _(self.error_code)

    @property
    def as_validationerror(self):
        return ValidationError(self.message, self.error_code, self.params)


class AccessDeniedException(AkaException):

    title = "common.error.access_denied"
