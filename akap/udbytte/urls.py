from django.urls import path
from udbytte.views import UdbytteView

app_name = "udbytte"

urlpatterns = [
    path(
        "",
        UdbytteView.as_view(),
        name="form",
    ),
]
