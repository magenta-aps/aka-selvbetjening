from django.urls import path
from fordring.views import (
    FordringReceiptView,
    InkassoGroupDataView,
    InkassoSagUploadView,
    InkassoSagView,
)

app_name = "fordring"

urlpatterns = [
    path("", InkassoSagView.as_view(), name="form"),
    path("upload/", InkassoSagUploadView.as_view(), name="upload"),
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
    path(
        "kvittering/<str:pdf_id>/",
        FordringReceiptView.as_view(),
        name="kvittering",
    ),
]
