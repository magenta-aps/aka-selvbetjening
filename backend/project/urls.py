from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

urlpatterns = [
    path("", include("aka.urls", namespace="aka")),
    path("obligatorisk_pension", include("obligatorisk_pension.urls", namespace="obligatorisk_pension")),
    path("", include("django_mitid_auth.urls", namespace="login")),
    path("_ht/", include("watchman.urls")),
]

if settings.MITID_TEST_ENABLED:
    urlpatterns.append(
        path("mitid_test/", include("mitid_test.urls", namespace="mitid_test"))
    )

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
