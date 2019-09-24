import logging

from aka.forms import InkassoForm
from aka.helpers.error import ErrorJsonResponse
from aka.helpers.prisme import Prisme
from django.http import JsonResponse
from django.views.generic.edit import BaseFormView

logger = logging.getLogger(__name__)


class InkassoSag(BaseFormView):

    form_class = InkassoForm

    def get(self, *args, **kwargs):
        return self.http_method_not_allowed(*args, **kwargs)

    def form_valid(self, form):
        prisme = Prisme(self.request)
        return JsonResponse(prisme.postClaim(form.cleaned_data, form.files))

    def form_invalid(self, form):
        return ErrorJsonResponse.from_error_dict(form.errors)
