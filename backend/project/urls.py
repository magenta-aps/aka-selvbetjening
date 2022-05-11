from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.urls import include

from sullissivik.login.views import LoginView, LoginCallbackView, LogoutView, LogoutCallbackView, MetadataView

urlpatterns = [
    url(r'saml/login/callback/?', LoginCallbackView.as_view(), name='saml-login-callback'),
    url(r'saml/login/?', LoginView.as_view(), name='saml-login'),
    url(r'saml/logout/callback/?', LogoutCallbackView.as_view(), name='saml-logout-callback'),
    url(r'saml/logout/?', LogoutView.as_view(), name='saml-logout'),
    url(r'saml/metadata/?', MetadataView.as_view(), name='saml-metadata'),
    url(r'^oid/', include('sullissivik.login.openid.urls', namespace='openid')),
    url(r'^nemid/', include('sullissivik.login.nemid.urls', namespace='nemid')),
    url(r'', include('aka.urls', namespace='aka')),
    url(r'^_ht/', include('watchman.urls')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
