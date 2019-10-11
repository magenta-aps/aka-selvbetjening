import logging

from aka.forms import InkassoForm
from aka.helpers.error import ErrorJsonResponse
from aka.helpers.prisme import Prisme
from aka.helpers.prisme import PrismeClaimRequest
from django.http import JsonResponse
from django.views.generic.edit import BaseFormView


logger = logging.getLogger(__name__)


class InkassoSag(BaseFormView):

    form_class = InkassoForm

    def get(self, *args, **kwargs):
        return self.http_method_not_allowed(*args, **kwargs)

    def form_valid(self, form):
        prisme = Prisme(self.request)
        testing = self.request.GET.get('testing') == '1'

        def get_codebtors(data):
            codebtors = []
            for i in range(1, 1000):
                if "meddebitor%d_cpr" % i in data:
                    codebtors.append(data["meddebitor%d_cpr" % i])
                elif "meddebitor%d_cvr" % i in data:
                    codebtors.append(data["meddebitor%d_cvr" % i])
                else:
                    break
            return codebtors

        claim = PrismeClaimRequest(
            claimant_id=form.cleaned_data.get('fordringshaver'),
            cpr_cvr=form.cleaned_data.get('debitor'),
            external_claimant=form.cleaned_data.get('fordringshaver2'),
            claim_group_number=form.cleaned_data.get('fordringsgruppe'),
            claim_type=form.cleaned_data.get('fordringstype'),
            child_cpr_cvr=form.cleaned_data.get('barns_cpr'),
            claim_ref=form.cleaned_data.get('ekstern_sagsnummer'),
            amount_balance=form.cleaned_data.get('hovedstol'),
            text=form.cleaned_data.get('hovedstol_posteringstekst'),
            created_by=form.cleaned_data.get('kontaktperson'),
            period_start=form.cleaned_data.get('periodestart'),
            period_end=form.cleaned_data.get('periodeslut'),
            due_date=form.cleaned_data.get('forfaldsdato'),
            founded_date=form.cleaned_data.get('betalingsdato'),
            obsolete_date=form.cleaned_data.get('foraeldelsesdato'),
            notes=form.cleaned_data.get('noter'),
            codebtors=get_codebtors(form.cleaned_data),
            files=[file for name, file in form.files.items()]
        )
        try:
            prisme_reply = prisme.create_claim(claim)[0]
            response = {
                'rec_id': prisme_reply.rec_id
            }
            if testing:
                response = {'request': claim.xml, 'response': response}
            return JsonResponse(response)
        except Exception as e:
            print(e)
            return ErrorJsonResponse.from_exception(e)

    def form_invalid(self, form):
        return ErrorJsonResponse.from_error_dict(form.errors)
