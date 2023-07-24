from django.urls import path
from rentenota.views import RenteNotaView

app_name = "rentenota"

urlpatterns = [
    path("", RenteNotaView.as_view(), name="form"),
]
