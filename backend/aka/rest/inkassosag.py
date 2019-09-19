import logging

from aka.helpers.prisme import Prisme
from django.http import JsonResponse
from django.views.generic import FormView

from aka.forms import InkassoForm
from django.views.generic.edit import BaseFormView

from aka.helpers.error import ErrorJsonResponse

logger = logging.getLogger(__name__)


class InkassoSag(BaseFormView):

    form_class = InkassoForm

    def form_valid(self, form):
        prisme = Prisme()
        value = prisme.postClaim(form.cleaned_data, form.files)
        return JsonResponse(value)

    def form_invalid(self, form):
        return ErrorJsonResponse(form.errors)
