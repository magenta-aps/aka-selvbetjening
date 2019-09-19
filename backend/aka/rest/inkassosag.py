import logging

from aka.forms import InkassoForm
from aka.helpers.error import ErrorJsonResponse
from aka.helpers.prisme import Prisme
from django.http import JsonResponse
from django.views.generic.edit import BaseFormView

logger = logging.getLogger(__name__)


class InkassoSag(BaseFormView):

    form_class = InkassoForm

    def form_valid(self, form):
        prisme = Prisme()
        value = prisme.postClaim(form.cleaned_data, form.files)
        return JsonResponse(value)

    def form_invalid(self, form):
        return ErrorJsonResponse(form.errors)
