from django.urls import path
from obligatorisk_pension.views import (
    ObligatoriskPensionCreateView,
    ObligatoriskPensionSkatteårView,
)

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
