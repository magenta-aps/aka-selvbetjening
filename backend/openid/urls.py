from django.conf.urls import include, url
from openid.views import Callback, Login, Logout, ErrorPage

urlpatterns = [
    url(r'^callback/$', Callback.as_view(), name='callback'),
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^logout/$', Logout.as_view(), name='logout'),
    url(r'^error/$', ErrorPage.as_view(), name='error'),
]