from django.conf.urls import include, url
from openid.views import Callback, Login, Logout

urlpatterns = [
    url(r'^callback/$', Callback.as_view(), name='callback'),
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^logout/$', Logout.as_view(), name='logout'),
]