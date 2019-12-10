from django.conf.urls import url
from sullissivik.login.openid.views import Callback, Login, Logout

app_name = 'sullissivik.login.openid'

urlpatterns = [
    url(r'^callback/$', Callback.as_view(), name='callback'),
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^logout/$', Logout.as_view(), name='logout'),
]
