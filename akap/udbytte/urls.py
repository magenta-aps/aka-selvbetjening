# SPDX-FileCopyrightText: 2023 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: MPL-2.0

from django.urls import path
from udbytte.api import api
from udbytte.views import UdbytteCreateView

app_name = "udbytte"

urlpatterns = [
    path(
        "",
        UdbytteCreateView.as_view(),
        name="form",
    ),
    path("api/", api.urls),
]
