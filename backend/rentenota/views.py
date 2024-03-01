from typing import List

from aka.clients.prisme import Prisme, PrismeException, PrismeInterestNoteRequest
from aka.utils import Cell, Field, Row
from django.utils.datetime_safe import date
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from project.view_mixins import (
    IsContentMixin,
    JsonRendererMixin,
    PdfRendererMixin,
    RequireCvrMixin,
    SimpleGetFormMixin,
    SpreadsheetRendererMixin,
)
from rentenota.forms import InterestNoteForm


# NY18
@method_decorator(csrf_exempt, name="dispatch")
class RenteNotaView(
    RequireCvrMixin,
    IsContentMixin,
    SimpleGetFormMixin,
    PdfRendererMixin,
    JsonRendererMixin,
    SpreadsheetRendererMixin,
    TemplateView,
):
    form_class = InterestNoteForm
    template_name = "rentenota/interestnote.html"
    pdf_template_name = "rentenota/interestnote_pdf.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = []
        self.items = []

    def get_journal_fields(self):
        return ["updated", "account_number", "interest_note", "billing_classification"]

    def get_transaction_fields(self):
        return [
            "voucher",
            "text",
            "due_date",
            "invoice_amount",
            "interest_amount",
            "transaction_date",
            "invoice",
            "calculate_from_date",
            "calculate_to_date",
            "interest_days",
        ]

    def get_fields(self) -> List[Field]:
        fields = [
            Field(name="updated", klass="nb"),
            Field(name="account_number", klass="nb"),
            Field(name="billing_classification", klass="nb"),
            Field(name="voucher", klass="nb"),
            Field(name="interest_note", klass="nb"),
            Field(name="text", klass=""),
            Field(name="due_date", klass="nb numbercell"),
            Field(name="invoice_amount", klass="nb numbercell", number=True),
            Field(name="interest_amount", klass="nb numbercell", number=True),
            Field(name="transaction_date", klass="nb numbercell"),
            Field(name="invoice", klass="nb"),
            Field(name="calculate_from_date", klass="nb numbercell"),
            Field(name="calculate_to_date", klass="nb numbercell"),
            Field(name="interest_days", klass="nb numbercell"),
        ]
        for field in fields:
            field.title = _("rentenota.%s" % field.name).replace("&shy;", "")
        return fields

    def load_items(self, form):
        prisme = Prisme()
        posts = []
        # Response is of type PrismeInterestNoteResponse
        # prisme.process_service handles mocking if necessary
        interest_note_data = prisme.process_service(
            PrismeInterestNoteRequest(
                self.cvr, form.cleaned_data["year"], form.cleaned_data["month"]
            ),
            "rentenota",
            self.cpr,
            self.cvr,
        )

        for interest_note_response in interest_note_data:
            for journal in interest_note_response.interest_journal:
                journaldata = {
                    key: getattr(journal, key) for key in self.get_journal_fields()
                }
                for transaction in journal.interest_transactions:
                    data = {
                        key: getattr(transaction, key)
                        for key in self.get_transaction_fields()
                    }
                    data.update(journaldata)
                    posts.append(data)
        self.items = posts

    def get_pages(self, key):
        return self.items

    def get_filename(self):
        return _("rentenota.filename").format(**dict(self.form.cleaned_data.items()))

    def get_sheetname(self):
        return "Rentenota"

    def get_rows(self):
        fields = self.get_fields()
        return [
            Row(cells=[Cell(field=field, value=item[field.name]) for field in fields])
            for item in self.items
        ]

    def form_valid(self, form):
        self.form = form
        try:
            self.load_items(form)
        except PrismeException as e:
            self.errors.append(e.as_error_dict)
        if "format" in self.request.GET:
            response = self.render()
            if response is not None:
                return response
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = {
            "date": date.today().strftime("%d/%m/%Y"),
            "items": self.items,
            "rows": self.get_rows(),
            "fields": self.get_fields(),
            "total": sum([float(item["interest_amount"]) for item in self.items])
            if self.items is not None
            else None,
            "errors": self.errors,
        }
        context.update(kwargs)
        return super().get_context_data(**context)
