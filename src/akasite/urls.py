from django.conf.urls import url

from akasite import views

app_name = 'akasite'

urlpatterns = [
    url(r'^index$', views.IndexView.as_view(), name='index'),
    url(r'^indberetning$', views.Indberetning.as_view(), name='indberetning'),
    url(r'^inkassosag$', views.InkassoSag.as_view(), name='inkassosag'),
    url(r'^debitor$', views.Debitor.as_view(), name='debitor'),
]
