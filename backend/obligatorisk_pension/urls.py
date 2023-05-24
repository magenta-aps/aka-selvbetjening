from django.urls import path
from obligatorisk_pension.views import ObligatoriskPensionCreateView

app_name = "obligatorisk_pension"

urlpatterns = [
    path(
        "",
        ObligatoriskPensionCreateView.as_view(),
        name="obligatorisk_pension_create",
    ),
]
