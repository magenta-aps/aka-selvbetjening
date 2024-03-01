from aka.views import (
    ChooseCvrView,
    CustomJavaScriptCatalog,
    IndexTemplateView,
    SetLanguageView,
)
from django.urls import path
from django.views.generic import TemplateView
from django_mitid_auth.saml.views import AccessDeniedView

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
