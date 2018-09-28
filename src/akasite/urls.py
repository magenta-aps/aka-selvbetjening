from django.conf.urls import url

from akasite.views import TestView

app_name = 'akasite'

urlpatterns = [
    url(r'^test', TestView.as_view(), name='test'),
]
