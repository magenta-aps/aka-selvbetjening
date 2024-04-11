from typing import Optional, Any

import logging
import uuid

from aka.clients.prisme import Prisme, PrismeException, PrismeImpairmentRequest
from aka.views import GetReceiptView
from django.core.exceptions import ValidationError
from django.forms import Form
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.datetime_safe import date
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import FormView
from nedskrivning.forms import NedskrivningForm, NedskrivningUploadForm
from project.view_mixins import ErrorHandlerMixin, IsContentMixin, RequireCvrMixin

logger = logging.getLogger(__name__)
# 6.4


class NedskrivningView(RequireCvrMixin, ErrorHandlerMixin, IsContentMixin, FormView):
    form_class: Optional[type[Any]] = NedskrivningForm
    template_name = "nedskrivning/form.html"

    def send_impairment(self, form):
        prisme = Prisme()
        if prisme.mock:
            return ["1234"]
        data = form if type(form) is dict else form.cleaned_data
        claimant = data["fordringshaver"] or self.claimant_ids[0]
        impairment = PrismeImpairmentRequest(
            # claimant_id=self.get_claimant_id(self.request),
            claimant_id=claimant,
            cpr_cvr=data.get("debitor"),
            claim_ref=data.get("ekstern_sagsnummer"),
            amount_balance=-abs(data.get("beloeb", 0)),
            claim_number_seq=data.get("sekvensnummer"),
        )
        return [
            x.rec_id
            for x in prisme.process_service(
                impairment, "nedskrivning", self.cpr, self.cvr
            )
        ]

    def form_valid(self, form):
        if len(self.claimant_ids) == 0:
            form.add_error(
                None,
                ValidationError(
                    _("login.error_no_claimants"), "login.error_no_claimants"
                ),
            )
            return self.form_invalid(form)
        pdf_id = None
        try:
            rec_ids = self.send_impairment(form)
            if rec_ids:
                pdf_id = self.store_pdf_context(
                    [{**form.cleaned_data, "rec_ids": rec_ids}]
                )
            return TemplateResponse(
                request=self.request,
                template="nedskrivning/success.html",
                context={
                    "rec_ids": rec_ids,
                    "upload": False,
                    "pdf_id": pdf_id,
                },
                using=self.template_engine,
            )
        except PrismeException as e:
            if e.code == 250 or e.code == "250":
                form.add_error(None, e.as_validationerror)
                return self.form_invalid(form)
            logger.info("Got error code %s from prisme" % str(e.code))
            raise e

    def store_pdf_context(self, data):
        now = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf_context = {
            "received_date": date.today(),
            "cvr": self.cvr,
            "lines": [
                {
                    "debitor": subdata.get("debitor"),
                    "ekstern_sagsnummer": subdata.get("ekstern_sagsnummer"),
                    "beloeb": -abs(subdata.get("beloeb", 0)),
                    "sekvensnummer": subdata.get("sekvensnummer"),
                    "rec_ids": subdata.get("rec_ids"),
                }
                for subdata in data
            ],
        }
        session = self.request.session
        if "receipts" not in session:
            session["receipts"] = {}
        pdf_id = str(uuid.uuid4())
        session["receipts"][pdf_id] = {
            "context": pdf_context,
            "filename": f"kvittering_nedskrivning_{now}.pdf",
            "template": "nedskrivning/receipt.html",
        }
        session.modified = True
        return pdf_id


class NedskrivningReceiptView(GetReceiptView):
    context = "nedskrivning"


class NedskrivningUploadView(NedskrivningView):
    form_class = NedskrivningUploadForm
    template_name = "nedskrivning/upload.html"
    parallel = False

    def handle_form(self, data):
        try:
            rec_ids = self.send_impairment(data)
            return {"rec_ids": rec_ids, **data}
        except PrismeException as e:
            logger.info(
                "Got error from prisme: %s %s for %s" % (str(e.code), e.text, str(data))
            )
            return {"error": e}

    def form_valid(self, form):
        if self.parallel:
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                results = list(
                    executor.map(
                        self.handle_form,
                        [subform.cleaned_data for subform in form.subforms],
                    )
                )
        else:
            results = [
                self.handle_form(subform.cleaned_data) for subform in form.subforms
            ]

        rec_ids = []
        responses = []
        errors = []
        for result in results:
            if "rec_ids" in result:
                rec_ids += result["rec_ids"]
                responses.append(result)
            if "error" in result:
                errors.append(result["error"].as_error_dict)

        pdf_id = None
        if responses:
            pdf_id = self.store_pdf_context(responses)

        return TemplateResponse(
            request=self.request,
            template="nedskrivning/success.html",
            context={
                "rec_ids": rec_ids,
                "errors": errors,
                "upload": True,
                "pdf_id": pdf_id,
            },
            using=self.template_engine,
        )
