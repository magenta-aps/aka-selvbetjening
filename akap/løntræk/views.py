import logging
import uuid

from aka.clients.prisme import (
    Prisme,
    PrismeException,
    PrismePayrollRequest,
    PrismePayrollRequestLine,
)
from aka.utils import get_ordereddict_key_index, spreadsheet_col_letter
from aka.views import GetReceiptView
from django.core.exceptions import ValidationError
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.datetime_safe import date
from django.views.generic.edit import FormView
from løntræk.forms import LoentraekForm, LoentraekFormSet, LoentraekUploadForm
from project.view_mixins import ErrorHandlerMixin, IsContentMixin, RequireCvrMixin

logger = logging.getLogger(__name__)


# 6.2
class LoentraekView(ErrorHandlerMixin, RequireCvrMixin, IsContentMixin, FormView):
    form_class = LoentraekForm
    template_name = "løntræk/form.html"

    def get_formset(self):
        return LoentraekFormSet(**self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **{
                **kwargs,
                "formset": self.get_formset(),
            }
        )

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        formset = self.get_formset()
        if form.is_valid() and formset.is_valid() and form.check_sum(formset, True):
            return self.form_valid(form, formset)
        return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        prisme = Prisme()
        try:
            payroll = PrismePayrollRequest(
                cvr=self.cvr,
                date=date(
                    int(form.cleaned_data["year"]),
                    int(form.cleaned_data["month"]),
                    1,
                ),
                received_date=date.today(),
                amount=form.cleaned_data["total_amount"],
                lines=[
                    PrismePayrollRequestLine(
                        subform.cleaned_data.get("cpr"),
                        subform.cleaned_data.get("agreement_number"),
                        subform.cleaned_data.get("amount"),
                        subform.cleaned_data.get("net_salary"),
                    )
                    for subform in formset
                    if subform.cleaned_data
                ],
            )
            rec_ids = [
                x.rec_id
                for x in prisme.process_service(
                    payroll, "loentraek", self.cpr, self.cvr
                )
            ]
            if rec_ids:
                pdf_id = self.store_pdf_context(
                    form.cleaned_data,
                    [subform.cleaned_data for subform in formset],
                    rec_ids,
                )
            return TemplateResponse(
                request=self.request,
                template="løntræk/success.html",
                context={
                    "rec_ids": rec_ids,
                    "pdf_id": pdf_id,
                },
                using=self.template_engine,
            )
        except PrismeException as e:
            found = False
            if e.code == 250 or e.code == "250":
                d = e.as_error_dict
                if "params" in d and "nr" in d["params"]:
                    for subform in formset:
                        if (
                            subform.cleaned_data.get("agreement_number")
                            == d["params"]["nr"]
                        ):
                            subform.add_error("agreement_number", e.as_validationerror)
                            found = True
            else:
                logger.info("Got error code %s from prisme" % str(e.code))
            if not found:
                form.add_error(None, e.as_validationerror)
            return self.form_invalid(form, formset)

    def form_invalid(self, form, formset):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

    def store_pdf_context(self, formdata, formsetdata, rec_ids):
        now = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf_context = {
            "received_date": date.today(),
            "date": {"year": int(formdata["year"]), "month": int(formdata["month"])},
            "total_amount": formdata["total_amount"],
            "rec_ids": rec_ids,
            "cvr": self.cvr,
            "lines": [
                {
                    "cpr": subformdata.get("cpr"),
                    "agreement_number": subformdata.get("agreement_number"),
                    "amount": subformdata.get("amount"),
                    "net_salary": subformdata.get("net_salary"),
                }
                for subformdata in formsetdata
            ],
        }
        session = self.request.session
        if "receipts" not in session:
            session["receipts"] = {}
        pdf_id = str(uuid.uuid4())
        session["receipts"][pdf_id] = {
            "context": pdf_context,
            "filename": f"kvittering_løntræk_{now}.pdf",
            "template": "løntræk/receipt.html",
        }
        session.modified = True
        return pdf_id


class LoentraekReceiptView(GetReceiptView):
    context = "loentraek"


class LoentraekUploadView(LoentraekView):
    form_class = LoentraekUploadForm
    template_name = "løntræk/upload.html"

    def forms_valid(self, forms):
        for subform in forms:
            if not subform.is_valid():
                return False
        return True

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            if self.forms_valid(form.subforms) and form.check_sum(form.subforms, True):
                return self.form_valid(form, form.subforms)
        return self.form_invalid(
            form, form.subforms if hasattr(form, "subforms") else None
        )

    def form_invalid(self, form, formset=None):
        if formset is not None:
            for row_index, subform in enumerate(formset, start=2):
                if subform.errors:
                    for field, errorlist in subform.errors.items():
                        try:
                            col_index = get_ordereddict_key_index(subform.fields, field)
                        except ValueError:
                            col_index = None
                        for error in errorlist.as_data():
                            form.add_error(
                                "file",
                                ValidationError(
                                    "error.upload_validation_item",
                                    code="error.upload_validation_item",
                                    params={
                                        "field": field,
                                        "message": str(error.message),
                                        "row": row_index,
                                        "col": col_index,
                                        "col_letter": spreadsheet_col_letter(col_index),
                                    },
                                ),
                            )
        return self.render_to_response(self.get_context_data(form=form))
