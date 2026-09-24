import json
import logging
from io import BytesIO

from aka.utils import render_pdf
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import Context, Engine
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.translation.trans_real import DjangoTranslation
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog
from project.view_mixins import (
    AkaMixin,
    ErrorHandlerMixin,
    HasUserMixin,
    RequireCvrMixin,
)


class CustomJavaScriptCatalog(JavaScriptCatalog):
    js_catalog_template = r"""
    {% autoescape off %}
    (function(globals) {
    var django = globals.django || (globals.django = {});
    django.catalog = django.catalog || {};
    {% if catalog_str %}
    django.catalog["{{ locale }}"] = {{ catalog_str }};
    {% endif %}
    }(this));
    {% endautoescape %}
    """

    def get(self, request, locale, *args, **kwargs):
        domain = kwargs.get("domain", self.domain)
        self.locale = locale
        # If packages are not provided, default to all installed packages, as
        # DjangoTranslation without localedirs harvests them all.
        packages = kwargs.get("packages", "")
        packages = packages.split("+") if packages else self.packages
        paths = self.get_paths(packages) if packages else None
        self.translation = DjangoTranslation(locale, domain=domain, localedirs=paths)
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = {"locale": self.locale}
        context.update(super(CustomJavaScriptCatalog, self).get_context_data(**kwargs))
        context["catalog_str"] = (
            json.dumps(context["catalog"], sort_keys=True, indent=2)
            if context["catalog"]
            else None
        )
        context["formats_str"] = json.dumps(
            context["formats"], sort_keys=True, indent=2
        )
        return context

    def render_to_response(self, context, **response_kwargs):
        template = Engine().from_string(self.js_catalog_template)
        return HttpResponse(
            template.render(Context(context)), 'text/javascript; charset="utf-8"'
        )


class SetLanguageView(View):
    def post(self, request, *args, **kwargs):
        language = request.POST.get("language", settings.LANGUAGE_CODE)
        translation.activate(language)
        # request.session[translation.LANGUAGE_SESSION_KEY] = language
        response = JsonResponse("OK", safe=False)
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            settings.LOCALE_MAP.get(language, language),
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            path=settings.LANGUAGE_COOKIE_PATH,
        )
        return response


class GetPDFView(ErrorHandlerMixin, RequireCvrMixin, View):
    def get(self, request, *args, **kwargs):
        pdf_id = kwargs["pdf_id"]
        try:
            pdf_context = request.session["receipts"][pdf_id]
        except KeyError:
            raise Http404
        return FileResponse(
            BytesIO(render_pdf(pdf_context["template"], pdf_context["context"])),
            filename=pdf_context["filename"],
            as_attachment=True,
        )


class GetReceiptView(GetPDFView):
    type = "receipts"


logger = logging.getLogger(__name__)


class IndexTemplateView(ErrorHandlerMixin, HasUserMixin, AkaMixin, TemplateView):
    template_name = "index.html"

    @method_decorator(ensure_csrf_cookie)
    def get(self, *args, **kwargs):
        return super(IndexTemplateView, self).get(*args, **kwargs)


class ChooseCvrView(AkaMixin, TemplateView):
    template_name = "choose_cvr.html"

    def get_context_data(self, **kwargs):
        context = {
            "cvrs": self.request.session.get("cvrs"),
            "back": self.request.GET.get("back"),
        }
        context.update(kwargs)
        return super().get_context_data(**context)

    def get(self, request, *args, **kwargs):
        cvr = request.GET.get("cvr")
        if cvr and cvr in self.request.session.get("cvrs"):
            back = self.request.GET.get("back")
            request.session["user_info"]["cvr"] = cvr
            request.session["has_checked_cvr"] = True
            request.session.save()
            return redirect(back)
        return super().get(request, *args, **kwargs)
