from django.conf.urls import url

from akasite import views

app_name = 'akasite'

urlpatterns = [
    url(r'^index$', views.IndexView.as_view(), name='index'),
    url(r'^indberetning$', views.Indberetning.as_view(), name='indberetning'),
]
