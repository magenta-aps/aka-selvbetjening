from django.conf.urls import url

from akasite.rest import inkassosag, rentenota
from akasite import htmlviews

app_name = 'akasite'

urlpatterns = [
    url(r'^index$', htmlviews.IndexView,
        name='index'),
    url(r'^inkassosag$', inkassosag.InkassoSag.as_view(),
        name='inkassosag'),
    url(r'^rentenota/from([0-9]{4}-[0-9]{2}-[0-9]{2})to([0-9]{4}-[0-9]{2}-[0-9]{2})$', rentenota.RenteNota.as_view(),
        name='rentenota (NY18)'),
]
