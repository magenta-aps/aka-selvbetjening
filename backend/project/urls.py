from typing import Union, List

from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, URLResolver, URLPattern

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path("", include("aka.urls", namespace="aka")),
    path(
        "obligatorisk_pension/",
        include("obligatorisk_pension.urls", namespace="obligatorisk_pension"),
    ),
    path("konto/", include("konto.urls", namespace="konto")),
    path("inkassosag/", include("fordring.urls", namespace="fordring")),
    path("loentraek/", include("løntræk.urls", namespace="løntræk")),
    path("nedskrivning/", include("nedskrivning.urls", namespace="nedskrivning")),
    path("rentenota/", include("rentenota.urls", namespace="rentenota")),
    path("udbytte/", include("udbytte.urls", namespace="udbytte")),
    path("", include("django_mitid_auth.urls", namespace="login")),
    path("_ht/", include("watchman.urls")),
]

if settings.MITID_TEST_ENABLED:
    urlpatterns.append(
        path("mitid_test/", include("mitid_test.urls", namespace="mitid_test"))
    )

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
