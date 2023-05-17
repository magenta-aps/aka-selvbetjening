from obligatorisk_pension.views import ObligatoriskPensionView
from django.urls import path

app_name = "obligatorisk_pension"

urlpatterns = [
    # Use 'django' domain instead of 'djangojs', so we get serverside translations
    path(
        "/",
        ObligatoriskPensionView.as_view(),
        name="obligatorisk_pension",
    ),
]
