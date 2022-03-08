from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.urls import include

urlpatterns = [
    url(r'^oid/', include('sullissivik.login.openid.urls', namespace='openid')),
    url(r'^nemid/', include('sullissivik.login.nemid.urls', namespace='nemid')),
    url(r'', include('aka.urls', namespace='aka')),
    url(r'^_ht/', include('watchman.urls')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
