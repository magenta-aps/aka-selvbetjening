from nedskrivning.views import NedskrivningReceiptView
from nedskrivning.views import NedskrivningView, NedskrivningUploadView
from django.urls import path

app_name = "nedskrivning"

urlpatterns = [
    path("", NedskrivningView.as_view(), name="form"),
    path(
        "upload/",
        NedskrivningUploadView.as_view(),
        name="upload",
    ),
    path(
        "kvittering/<str:pdf_id>/",
        NedskrivningReceiptView.as_view(),
        name="kvittering",
    ),
]
