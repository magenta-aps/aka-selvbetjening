import sys
from aka.clients.prisme import (
    PrismeSELRequest,
    PrismeAKIRequest,
    PrismeSELTotalRequest,
    PrismeAKITotalRequest,
    PrismeException,
    Prisme,
)
from aka.utils import Field, Cell, Row
from aka.utils import Table, chunks
from aka.views import logger
from django.urls import reverse
from django.utils.datetime_safe import date
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _, gettext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from konto.forms import KontoForm
from project.view_mixins import (
    HasUserMixin,
    SimpleGetFormMixin,
    PdfRendererMixin,
    JsonRendererMixin,
    SpreadsheetRendererMixin,
    IsContentMixin,
)
from typing import List


@method_decorator(csrf_exempt, name="dispatch")
class KontoView(
    HasUserMixin,
    SimpleGetFormMixin,
    PdfRendererMixin,
    JsonRendererMixin,
    SpreadsheetRendererMixin,
    IsContentMixin,
    TemplateView,
):
    form_class = KontoForm
    template_name = "konto/konto.html"
    pdf_template_name = "konto/pdf.html"
    available_keys = (
        "sel",
        "aki",
    )
    authority = {
        "title": "Namminersorlutik Oqartussat - Grønlands Selvstyre",
        "lines": ["Akileraartarnermut Aqutsisoqarfik", "Skattestyrelsen"],
        "pane_titles": {
            "sel": "title_sel",
            "aki": "title_aki",
        },
    }

    def get_organization_data(self):
        return {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sections = None
        self._data = {}
        self._total = {}
        self._prisme = None

    def form_valid(self, form):
        self.form = form
        try:
            self.load_sections(form)
        except PrismeException as e:
            form.add_error(None, e.as_validationerror)
            return self.form_invalid(form)
        if "format" in self.request.GET:
            response = self.render()
            if response is not None:
                return response
        return super(KontoView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["cprcvr_choices"] = [
            (getattr(self, c), "%s: %s" % (c.upper(), getattr(self, c)))
            for c in ("cpr", "cvr")
            if getattr(self, c)
        ]
        kwargs["initial"]["open_closed"] = 2
        return kwargs

    def get_context_data(self, **kwargs):
        context = {}
        if self.form.is_bound:
            formdata = self.form.cleaned_data
            context.update(
                {
                    "sections": self.sections,
                    "date": date.today().strftime("%d/%m/%Y"),
                    "period": {
                        "from_date": formdata["from_date"].strftime("%d-%m-%Y")
                        if formdata.get("from_date") is not None
                        else None,
                        "to_date": formdata["to_date"].strftime("%d-%m-%Y")
                        if formdata.get("to_date") is not None
                        else None,
                    },
                    "cprcvr": self.cprcvr_choice,
                    "authority": self.authority,
                    "organization": self.get_organization_data(),
                }
            )
            if self.is_pdf:
                context["pages"] = self.get_pages()

        context.update(kwargs)
        return super().get_context_data(**context)

    def get_filename(self):
        try:
            from_date = self.form.cleaned_data["from_date"].strftime("%Y-%m-%d")
        except (KeyError, ValueError, AttributeError):
            from_date = ""
        try:
            to_date = self.form.cleaned_data["to_date"].strftime("%Y-%m-%d")
        except (KeyError, ValueError, AttributeError):
            to_date = ""
        return _("konto.filename").format(from_date=from_date, to_date=to_date)

    def get_sheetname(self):
        return "Kontoudtog"

    def hide_fields(self, form, fields):
        return [
            field for field in fields if field.name not in form.cleaned_data["hidden"]
        ]

    @property
    def prisme(self):
        if not self._prisme:
            self._prisme = Prisme()
        return self._prisme

    def get_lookup_class(self, key):
        if key == "sel":
            return PrismeSELRequest
        if key == "aki":
            return PrismeAKIRequest

    def get_total_lookup_class(self, key):
        if key == "sel":
            return PrismeSELTotalRequest
        if key == "aki":
            return PrismeAKITotalRequest

    @property
    def cprcvr_choice(self):
        cprcvr = str(self.form.cleaned_data.get("cprcvr") or self.cpr or self.cvr)
        if cprcvr == str(self.cpr):
            return (cprcvr, "cpr")
        elif cprcvr == str(self.cvr):
            return (cprcvr, "cvr")
        else:
            logger.info(
                "cprcvr_choice got: "
                + str({"cprcvr": cprcvr, "cpr": self.cpr, "cvr": self.cvr})
            )

    def accept_debitor_group_id(self, debitor_group_id: str) -> bool:
        return True

    def get_rows_by_key(self, key: str) -> List[Row]:
        if key not in self._data:
            try:
                (cprcvr, c) = self.cprcvr_choice
                lookup_class = self.get_lookup_class(key)
                prisme_reply = self.prisme.process_service(
                    lookup_class(
                        cprcvr,
                        self.form.cleaned_data["from_date"],
                        self.form.cleaned_data["to_date"],
                        self.form.cleaned_data["open_closed"],
                    ),
                    "account",
                    self.cpr,
                    self.cvr,
                )
                self._data[key] = []
                if len(prisme_reply) == 0:
                    return []
                for entry in prisme_reply[0]:
                    # entry is of type PrismeAccountResponseTransaction
                    if self.accept_debitor_group_id(entry.debitor_group_id):
                        row = Row()
                        for field in self.get_fields_by_key(key):
                            value = getattr(entry, field.name)
                            if field.modifier:
                                value = field.modifier(value)
                            row.cells.append(
                                Cell(
                                    field=field,
                                    value=value,
                                )
                            )
                        self._data[key].append(row)
            except PrismeException:
                pass
        return self._data.get(key, [])

    def get_total_data(self, key: str) -> dict:
        if key not in self._total:
            try:
                (cprcvr, c) = self.cprcvr_choice
                lookup_class = self.get_total_lookup_class(key)
                prisme_reply = self.prisme.process_service(
                    lookup_class(cprcvr), "account", self.cpr, self.cvr
                )
                if len(prisme_reply) == 0:
                    return None
                reply = prisme_reply[0]
                self._total[key] = {
                    key: getattr(reply, key)
                    for key in [
                        "total_claim",
                        "total_payment",
                        "total_sum",
                        "total_restance",
                    ]
                }
            except PrismeException:
                pass
        return self._total.get(key)

    def load_sections(self, form):
        self.sections = []
        key = self.request.GET.get("key")
        keys = [key] if key and key in self.available_keys else self.available_keys
        for key in keys:
            rows = self.get_rows_by_key(key)
            total = self.get_total_data(key)
            self.sections.append(
                {
                    "key": key,
                    "title": "konto." + self.authority["pane_titles"][key],
                    "fields": self.get_fields_by_key(key),
                    "rows": rows,
                    "total": total,
                }
            )

    def get_pages(self, key: str = None):
        if key is None:
            key = self.request.GET.get("key")
        if key and key in self.available_keys:
            pages = []
            max_columns_per_page = (
                8  # if there are more columns than this number, we do a split
            )
            line_field = Field(
                name="index", klass="nb", transkey="konto.linje", title="Linje"
            )
            for section in self.sections:
                total = section["total"]
                if len(section["rows"]):
                    # item_collection is a dict of all items for a key (key = 'aki' or 'sel')
                    # it contains title, fields, total, and a list of rows
                    # Read fields in chunks, creating a new page for each chunk
                    for page_fields, startcol in chunks(
                        section["fields"], max_columns_per_page
                    ):
                        pages.append(
                            Table(
                                name=section["key"],
                                fields=[line_field] + page_fields,
                                rows=[
                                    Row(
                                        cells=[Cell(field=line_field, value=rownumber)]
                                        + row.cells[
                                            startcol : startcol + max_columns_per_page
                                        ]
                                    )
                                    for rownumber, row in enumerate(section["rows"], 1)
                                ],
                                total=total,
                            )
                        )

                        # Only show totals in first page of the section
                        total = None
                else:
                    pages.append(
                        Table(
                            name=section["key"], fields=[line_field] + section["fields"]
                        )
                    )
            return pages
        return []

    def get_rows(self) -> List[Row]:
        return self.get_rows_by_key(self.key)

    def get_extra(self) -> dict:
        total = self.get_total_data(self.key)
        if total:
            return {
                gettext("konto.%s" % x): total[x]
                for x in ["total_claim", "total_payment", "total_sum", "total_restance"]
            }

    def get_fields(self) -> List[Field]:
        return self.get_fields_by_key(self.key)

    def get_fields_by_key(self, key: str = "sel") -> List[Field]:
        fields = [
            Field(name="account_number", klass="nb"),
            Field(name="transaction_date", klass="nb"),
            Field(name="accounting_date", klass="nb"),
            Field(name="debitor_group_id", klass="nb"),
            Field(name="debitor_group_name", klass="nb"),
            Field(name="voucher", klass="nb"),
            Field(name="text", klass=""),
            Field(name="payment_code", klass="nb"),
            Field(name="payment_code_name", klass="nb"),
            Field(name="amount", klass="nb numbercell", number=True),
            Field(name="remaining_amount", klass="nb numbercell", number=True),
            Field(name="due_date", klass="nb"),
            Field(name="closed_date", klass="nb"),
            Field(name="last_settlement_voucher", klass="nb"),
            Field(name="collection_letter_date", klass="nb"),
            Field(name="collection_letter_code", klass="nb"),
            Field(name="claim_type_code", klass="nb"),
            Field(name="invoice_number", klass="nb"),
            Field(name="transaction_type", klass="nb"),
            Field(name="child_claimant", klass="nb"),
        ]
        if key == "sel":
            fields += [
                Field(
                    name="claim_type_code",
                    labelkey="submitted_to_claims",
                    klass="nb",
                    modifier=lambda d: (d == "INDR"),
                    boolean=True,
                ),
                Field(name="rate_number", klass="nb"),
            ]
        for field in fields:
            field.transkey = "konto.%s" % (field.labelkey or field.name)
            field.title = _(field.transkey).replace("&shy;", "")
        return fields


class DebitorKontoRangeRestricted:
    debitor_group_id_range = (0, sys.maxsize)

    def accept_debitor_group_id(self, debitor_group_id: str) -> bool:
        try:
            debitor_group_id_int = int(debitor_group_id or "0")
        except ValueError:
            return False
        if (
            self.debitor_group_id_range[0]
            <= debitor_group_id_int
            <= self.debitor_group_id_range[1]
        ):
            return True
        return False


class AKAKontoView(DebitorKontoRangeRestricted, KontoView):
    available_keys = (
        "aki",
        "sel",
    )
    debitor_group_id_range = (200000, 999999)

    def get_organization_data(self):
        return {
            "phone",
            "fax",
            "swift",
            "iban",
            "cvrse",
            "account",
        }


class DCRKontoView(DebitorKontoRangeRestricted, KontoView):
    available_keys = ("sel",)
    debitor_group_id_range = (1000, 199999)
    authority = {
        "title": "Namminersorlutik Oqartussat - Grønlands Selvstyre",
        "lines": [
            "Qitiusumik Naatsorsuuserisoqarfik",
            "Den centrale Regnskabsafdeling",
        ],
        "pane_titles": {
            "sel": "title_sel_dcr",
            "aki": "title_aki",
        },
    }

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **{
                **kwargs,
                "regnskabskontor_note": True,
                "konto_href_obj": {"href": reverse("konto:konto")},
            }
        )

    def get_extra(self) -> dict:
        return {}

    def get_organization_data(self):
        return {
            "phone": "+299 34 55 68",
            "email": "Debitor@nanoq.gl",
            "swift": "GRENGLGX",
            "iban": "GL5864710001023850",
            "cvrse": "19785289",
            "account": "6471-1023850",
        }

    def get_total_data(self, key: str):
        return {}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {
            "hidden": [
                "sel.transaction_date",
                "sel.accounting_date",
                "sel.voucher",
                "sel.payment_code",
                "sel.payment_code_name",
                "sel.closed_date",
                "sel.last_settlement_voucher",
                "sel.collection_letter_date",
                "sel.collection_letter_code",
                "sel.claim_type_code",
                "sel.transaction_type",
            ]
        }
        return kwargs

    # Begrænser regneark-output (feltnavne) til de valgte kolonner
    # Skal muligvis flyttes til KontoView
    def get_spreadsheet_fields(self):
        hidden = self.form.cleaned_data["hidden"]
        return filter(
            lambda field: f"{self.key}.{field.label}" not in hidden, self.get_fields()
        )

    # Begrænser regneark-output (rækkeindhold) til de valgte kolonner
    # Skal muligvis flyttes til KontoView
    def get_spreadsheet_rows(self):
        hidden = self.form.cleaned_data["hidden"]
        rows = []
        for row in self.get_rows():
            rows.append(
                Row(
                    cells=list(
                        filter(
                            lambda cell: f"{self.key}.{cell.field.label}" not in hidden,
                            row.cells,
                        )
                    )
                )
            )
        return rows
