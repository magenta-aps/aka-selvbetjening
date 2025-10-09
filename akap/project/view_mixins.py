import json
import os
from functools import cached_property
from io import BytesIO

import pandas as pd
from aka.clients.dafo import Dafo
from aka.clients.prisme import Prisme, PrismeCvrCheckRequest, PrismeNotFoundException
from aka.exceptions import AkaException
from aka.models import PrismeDown
from aka.utils import flatten, render_pdf
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext
from django.views.generic.edit import FormMixin
from requests import ReadTimeout
from requests.exceptions import SSLError


class ErrorHandlerMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except AkaException as e:
            return TemplateResponse(
                request=request,
                template="aka/util/error.html",
                context={
                    "header": e.title,
                    "message": e.message,
                    "error_code": e.error_code,
                    "error_params": json.dumps(e.params),
                },
                using=self.template_engine,
            )


class HasUserMixin(object):
    def __init__(self, *args, **kwargs):
        self.cvr = None
        self.cpr = None
        self.claimant_ids = []
        self.company = None
        self.person = None
        super().__init__(*args, **kwargs)

    def get_claimants(self, request):
        if "claimantIds" in request.session:
            return request.session["claimantIds"]
        elif self.cvr is not None:
            try:
                cvr = self.cvr
                prisme = Prisme()
                if prisme.mock:
                    return ["1234"]
                claimant_ids = flatten(
                    [
                        response.claimant_id
                        for response in prisme.process_service(
                            PrismeCvrCheckRequest(cvr), "cvr_check", self.cpr, self.cvr
                        )
                    ]
                )
                request.session["claimantIds"] = claimant_ids
                request.session.save()
                return claimant_ids
            except (PrismeNotFoundException, AttributeError):
                return []
        else:
            return []

    def get_company(self, request):
        if "company" in request.session["user_info"]:
            return request.session["user_info"]["company"]
        elif self.cvr is not None:
            try:
                company = Dafo().lookup_cvr(self.cvr)
                request.session["user_info"]["company"] = company
                return company
            except Exception:
                pass

    def get_person(self, request):
        if "person" in request.session["user_info"]:
            return request.session["user_info"]["person"]
        elif self.cpr is not None:
            try:
                person = Dafo().lookup_cpr(self.cpr, False)
                request.session["user_info"]["person"] = person
                return person
            except Exception:
                pass

    def obtain_cvr(self, request):
        try:
            self.cvr = request.session["user_info"].get("cvr", None)
            if self.cvr is None:
                self.cvr = request.session["user_info"].get("CVR", None)
        except (KeyError, TypeError, AttributeError, ValueError):
            pass
        print(f"Got CVR from MitID: {self.cvr}")

        if (
            self.cpr
            and not self.cvr
            and not request.session.get("has_checked_cvr")
            and not settings.DEBUG
        ):
            try:
                cvrs = Dafo().lookup_cvr_by_cpr(self.cpr, False)
                if cvrs is not None:
                    if len(cvrs) > 1:
                        request.session["cvrs"] = [str(x) for x in cvrs]
                        request.session.save()
                        return redirect(
                            reverse("aka:choose_cvr")
                            + "?back="
                            + request.get_full_path()
                        )
                    if len(cvrs) == 1:
                        self.cvr = request.session["user_info"]["cvr"] = cvrs[0]
                    print(f"Got CVR from Dafo: {self.cvr}")
                request.session["has_checked_cvr"] = True
                request.session.save()
            except ReadTimeout:
                pass

        if not self.cvr and settings.DEFAULT_CVR:
            self.cvr = settings.DEFAULT_CVR

        if self.cvr:
            self.claimant_ids = self.get_claimants(request)
            self.company = self.get_company(request)

    def dispatch(self, request, *args, **kwargs):
        if (
            settings.PRISME_CONNECT["mock"]
            or "test.erp.gl" in settings.PRISME_CONNECT["wsdl_file"]
        ) and "cpr" in request.GET:
            self.cpr = request.GET["cpr"]
        else:
            try:
                self.cpr = request.session["user_info"].get("cpr", None)
                if self.cpr is None:
                    self.cpr = request.session["user_info"]["CPR"]
                p = self.get_person(request)
                p["navn"] = " ".join([x for x in [p["fornavn"], p["efternavn"]] if x])
                self.person = p
            except (KeyError, TypeError):
                pass

            if not self.cpr and settings.DEFAULT_CPR:
                self.cpr = settings.DEFAULT_CPR

        if (
            settings.PRISME_CONNECT["mock"]
            or "test.erp.gl" in settings.PRISME_CONNECT["wsdl_file"]
        ) and "cvr" in request.GET:
            self.cvr = request.GET["cvr"]
            has_cvr = True
        else:
            has_cvr = "user_info" in request.session and (
                "cvr" in request.session["user_info"]
                or "CVR" in request.session["user_info"]
            )
            try:
                self.obtain_cvr(request)
                if not has_cvr and "cvrs" in request.session:
                    has_cvr = True
            except SSLError:
                return TemplateResponse(
                    request, "aka/downtime.html", {"has_cvr": has_cvr}
                )

        if PrismeDown.get():
            return TemplateResponse(request, "aka/downtime.html", {"has_cvr": has_cvr})
        try:
            return super().dispatch(request, *args, **kwargs)
        except SSLError:
            return TemplateResponse(request, "aka/downtime.html", {"has_cvr": has_cvr})

    def get_context_data(self, **kwargs):
        context = {
            "cpr": self.cpr,
            "cvr": self.cvr,
            "claimant_ids": self.claimant_ids,
            "company": self.company,
            "person": self.person,
            "logged_in": {
                "navn": " | ".join(
                    [
                        x["navn"]
                        for x in [self.person, self.company]
                        if x is not None and "navn" in x
                    ]
                )
            },
        }
        context.update(kwargs)
        return super().get_context_data(**context)


class RequireCprMixin(HasUserMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            self.cpr = request.session["user_info"]["cpr"]
        except (KeyError, TypeError):
            if settings.DEFAULT_CPR:
                self.cvr = settings.DEFAULT_CPR
            else:
                raise PermissionDenied("no_cpr")
        return super().dispatch(request, *args, **kwargs)


class RequireCvrMixin(HasUserMixin):
    def dispatch(self, request, *args, **kwargs):
        self.obtain_cvr(request)
        if not self.cvr:
            raise PermissionDenied("no_cvr")
        return super().dispatch(request, *args, **kwargs)


class SimpleGetFormMixin(FormMixin):
    def get(self, request, *args, **kwargs):
        form = self.form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return super().get(self.request)

    # def form_invalid(self, form):
    #     return super().get(self.request)

    def get_form_kwargs(self):
        kwargs = {
            "initial": self.get_initial(),
            "prefix": self.get_prefix(),
        }
        if self.request.method in ("GET") and len(self.request.GET):
            kwargs.update(
                {
                    "data": self.request.GET,
                }
            )
        return kwargs


class AkaMixin(object):
    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **dict({"locale_map": settings.LOCALE_MAP}, **kwargs)
        )


class IsContentMixin(AkaMixin):
    def get_context_data(self, **kwargs):
        return super().get_context_data(**dict({"is_content": True}, **kwargs))


class RendererMixin(object):
    def render(self):
        pass

    @property
    def format(self):
        return self.request.GET.get("format")

    @property
    def accepted_formats(self):
        return []

    @property
    def key(self):
        return self.request.GET.get("key")

    def format_url(self, format, **kwargs):
        params = self.request.GET.copy()
        params["format"] = format
        params.update(kwargs)
        return self.request.path + "?" + params.urlencode()

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **dict(
                {
                    ("%slink" % format): self.format_url(format, key=self.key)
                    for format in self.accepted_formats
                },
                **kwargs,
            )
        )


class PdfRendererMixin(RendererMixin):
    pdf_template_name = ""

    pdf_css_files = ["css/output.css", "css/print.css", "css/pdf.css"]

    def get_filename(self):
        raise NotImplementedError

    @property
    def accepted_formats(self):
        return super().accepted_formats + ["pdf"]

    @cached_property
    def is_pdf(self):
        return self.format == "pdf"

    def render(self, context=None, wrap_in_response=True):
        if self.is_pdf:
            if context is None:
                context = self.get_context_data()
            css_data = []
            for css_file in self.pdf_css_files:
                css_static_path = css_file.split("/")
                css_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "static",
                    *css_static_path,
                )
                if not os.path.exists(css_path):
                    css_path = os.path.join(settings.STATIC_ROOT, *css_static_path)
                with open(css_path) as file:
                    css_data.append(file.read())
            context["css"] = "".join(css_data)

            html = False
            if html:
                html_data = get_template(self.pdf_template_name).render(context)
                return HttpResponse(html_data) if wrap_in_response else html_data
            else:
                pdf_data = render_pdf(
                    self.pdf_template_name,
                    context,
                    lambda html: html.replace(
                        '"%s' % settings.STATIC_URL,
                        '"file://%s/' % os.path.abspath(settings.STATIC_ROOT),
                    ),
                )
                if wrap_in_response:
                    response = HttpResponse(pdf_data, content_type="application/pdf")
                    response["Content-Disposition"] = (
                        f'attachment; filename="{self.get_filename()}.pdf"'
                    )
                    return response
                else:
                    return pdf_data

        return super().render()

    def get_context_data(self, **kwargs):
        return super().get_context_data(**dict({"pdf": self.is_pdf}, **kwargs))

    def form_invalid(self, form):
        if self.is_pdf:
            return self.render()
        return super().form_invalid(form)


class JsonRendererMixin(RendererMixin):
    @property
    def accepted_formats(self):
        return super().accepted_formats + ["json"]

    def render(self):
        if self.format == "json":
            fields = self.get_fields(self.key)  # List of dicts
            items = self.get_data(self.key)  # List of dicts
            data = {
                "count": len(items),
                "items": [
                    {field["name"]: getattr(item, field["name"]) for field in fields}
                    for item in items
                ],
            }
            return JsonResponse(data)
        return super().render()


class SpreadsheetRendererMixin(RendererMixin):

    type_map = {
        "xlsx": {
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "engine": "xlsxwriter",
        },
        "ods": {
            "content_type": "application/vnd.oasis.opendocument.spreadsheet",
            "engine": "odf",
        },
        "csv": {"content_type": "text/csv", "engine": "csv"},
    }

    def get_filename(self):
        raise NotImplementedError

    def get_sheetname(self):
        return "Sheet 1"

    def get_extra(self):
        return None

    @property
    def accepted_formats(self):
        return super().accepted_formats + ["xlsx", "ods", "csv"]

    def get_spreadsheet_fields(self):
        return self.get_fields()

    def get_spreadsheet_rows(self):
        return self.get_rows()

    def get_spreadsheet_extra(self):
        return self.get_extra()

    def render(self):
        format = self.format
        if format in self.accepted_formats:
            engine = self.type_map[format]["engine"]
            content_type = self.type_map[format]["content_type"]

            fields = self.get_spreadsheet_fields()  # List of Fields
            rows = self.get_spreadsheet_rows()  # List of Rows
            extra = self.get_spreadsheet_extra()  # List of Rows

            data = []
            headers = [field.title or field.name for field in fields]

            for row in rows:
                for cell in row.cells:
                    if cell.field.boolean:
                        cell.value = gettext("ja") if cell.value else gettext("nej")
                data.append([cell.value for cell in row.cells])

            if extra is not None:
                data += [[]] + [[key, value] for key, value in extra.items()]

            df = pd.DataFrame(data, columns=headers)

            buffer = BytesIO()
            if format == "csv":
                df.to_csv(buffer, mode="wb", sep=";")
            else:
                with pd.ExcelWriter(buffer, engine=engine) as writer:
                    df.to_excel(writer, sheet_name=self.get_sheetname())
            buffer.seek(0)
            return FileResponse(
                streaming_content=buffer,
                as_attachment=True,
                headers={
                    "Content-Type": content_type,
                    "Content-Disposition": "attachment; filename="
                    + self.get_filename(),
                },
                filename="%s.%s" % (self.get_filename(), format),
            )
        return super().render()
