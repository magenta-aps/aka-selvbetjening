from django.urls import path
from konto.views import AKAKontoView, DCRKontoView

app_name = "konto"

urlpatterns = [
    path("", AKAKontoView.as_view(), name="konto"),
    path("sel/", DCRKontoView.as_view(), name="dcrkonto"),
]
