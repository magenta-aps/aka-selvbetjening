from django.conf import settings
from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

urlpatterns = [
    url(r'', include('aka.urls', namespace='aka')),
    path('', include('django_mitid_auth.urls', namespace='login')),
    url(r'^_ht/', include('watchman.urls')),
]

if settings.MITID_TEST_ENABLED:
    urlpatterns.append(
        url('mitid_test', include('mitid_test.urls', namespace='mitid_test'))
    )

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
