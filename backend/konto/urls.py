from django.urls import path
from konto.views import KontoView
from konto.views import SELKontoView

app_name = "konto"

urlpatterns = [
    path("", KontoView.as_view(), name="konto"),
    path("sel/", SELKontoView.as_view(), name="selkonto"),
]
