from django.urls import path
from django.views.generic import TemplateView
from obligatorisk_pension.views import ObligatoriskPensionCreateView

from obligatorisk_pension.views import ObligatoriskPensionSkatteårView

app_name = "obligatorisk_pension"

urlpatterns = [
    path(
        "",
        ObligatoriskPensionSkatteårView.as_view(),
        name="create_skatteår",
    ),
    path(
        "<int:skatteår>",
        ObligatoriskPensionCreateView.as_view(),
        name="create",
    ),
]
