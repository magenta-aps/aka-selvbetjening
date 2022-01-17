from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = [
    url(r'^oid/', include('sullissivik.login.openid.urls', namespace='openid')),
    url(r'^nemid/', include('sullissivik.login.nemid.urls', namespace='nemid')),
    url(r'', include('aka.urls', namespace='aka')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
