import logging

from aka.forms import LoentraekForm
from aka.helpers.error import ErrorJsonResponse
from aka.helpers.prisme import Prisme
# When the service is implemented unused imports should be removed,
# but until then they are just commented out as a reference
from django.http import JsonResponse
# from aka.helpers.result import Error, Success
# from aka.helpers.sharedfiles import getSharedJson
from django.views.generic.edit import BaseFormView

logger = logging.getLogger(__name__)


class LoenTraek(BaseFormView):
    '''This class handles the REST interface at /loentraek

    The purpose is to report pay deductions to Prisme.
    '''

    def get(self, *args, **kwargs):
        return self.http_method_not_allowed(*args, **kwargs)

    form_class = LoentraekForm

    def form_valid(self, form):
        prisme = Prisme()
        value = {}  # some call to prisme
        return JsonResponse(value)

    def form_invalid(self, form):
        return ErrorJsonResponse.from_error_dict(form.errors)
