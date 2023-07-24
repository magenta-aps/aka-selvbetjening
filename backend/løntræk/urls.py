from løntræk.views import LoentraekReceiptView
from løntræk.views import LoentraekView, LoentraekUploadView
from django.urls import path

app_name = "løntræk"

urlpatterns = [
    # Use 'django' domain instead of 'djangojs', so we get serverside translations
    path("", LoentraekView.as_view(), name="form"),
    path("upload/", LoentraekUploadView.as_view(), name="upload"),
    path(
        "kvittering/<str:pdf_id>/",
        LoentraekReceiptView.as_view(),
        name="kvittering",
    ),
]
