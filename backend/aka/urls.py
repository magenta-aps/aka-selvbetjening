from aka.views import ChooseCvrView
from aka.views import CustomJavaScriptCatalog, SetLanguageView
from aka.views import IndexTemplateView
from aka.views import InkassoGroupDataView
from aka.views import InkassoSagView, InkassoSagUploadView
from aka.views import LoentraekReceiptView, FordringReceiptView, NedskrivningReceiptView
from aka.views import LoentraekView, LoentraekUploadView
from aka.views import NedskrivningView, NedskrivningUploadView
from aka.views import RenteNotaView
from aka.views import UdbytteView
from django.urls import path
from django_mitid_auth.saml.views import AccessDeniedView
from django.views.generic import TemplateView

app_name = "aka"

urlpatterns = [
    # Use 'django' domain instead of 'djangojs', so we get serverside translations
    path(
        "language/<str:locale>/",
        CustomJavaScriptCatalog.as_view(domain="django", packages=["aka"]),
        name="javascript-language-catalog",
    ),
    path("language/", SetLanguageView.as_view(), name="set-language"),
    path("", IndexTemplateView.as_view(), name="index"),
    path("choose_cvr/", ChooseCvrView.as_view(), name="choose_cvr"),
    path(
        "prisme-down/",
        TemplateView.as_view(template_name="aka/downtime.html"),
        name="downtime",
    ),
    path("inkassosag/", InkassoSagView.as_view(), name="inkassosag"),
    path(
        "inkassosag/upload/", InkassoSagUploadView.as_view(), name="inkassosag-upload"
    ),
    path(
        "fordringsgrupper/<str:var>/",
        InkassoGroupDataView.as_view(),
        name="fordringsgrupper-var",
    ),
    path(
        "fordringsgrupper/",
        InkassoGroupDataView.as_view(),
        name="fordringsgrupper",
    ),
    path("loentraek/", LoentraekView.as_view(), name="loentraek"),
    path("loentraek/upload/", LoentraekUploadView.as_view(), name="loentraek-upload"),
    path("rentenota/", RenteNotaView.as_view(), name="rentenota"),
    path("nedskrivning/", NedskrivningView.as_view(), name="nedskrivning"),
    path(
        "nedskrivning/upload/",
        NedskrivningUploadView.as_view(),
        name="nedskrivning-upload",
    ),
    path(
        "loentraek/kvittering/<str:pdf_id>/",
        LoentraekReceiptView.as_view(),
        name="loentraek-kvittering",
    ),
    path(
        "inkassosag/kvittering/<str:pdf_id>/",
        FordringReceiptView.as_view(),
        name="inkassosag-kvittering",
    ),
    path(
        "nedskrivning/kvittering/<str:pdf_id>/",
        NedskrivningReceiptView.as_view(),
        name="nedskrivning-kvittering",
    ),
    path(
        "udbytte/",
        UdbytteView.as_view(),
        name="udbytte",
    ),
    path(
        "error/login-timeout/",
        AccessDeniedView.as_view(template_name="aka/error/login_timeout.html"),
        name="login-timeout",
    ),
    path(
        "error/login-repeat/",
        AccessDeniedView.as_view(template_name="aka/error/login_repeat.html"),
        name="login-repeat",
    ),
    path(
        "error/login-nocprcvr/",
        AccessDeniedView.as_view(template_name="aka/error/login_no_cprcvr.html"),
        name="login-no-cprcvr",
    ),
    path(
        "downtime", TemplateView.as_view(template_name="downtime.html"), name="downtime"
    ),
]
