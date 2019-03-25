from django.conf.urls import include, url
from openid.views import Callback, Login

urlpatterns = [
    url(r'^callback/$', Callback.as_view(), name='callback'),
    url(r'^login/$', Login.as_view(), name='login'),
]