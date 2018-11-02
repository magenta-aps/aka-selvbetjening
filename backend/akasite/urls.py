from django.conf.urls import url

from akasite.rest import inkassosag, fileupload, rentenota
from akasite import htmlviews

app_name = 'akasite'

urlpatterns = [
    url(r'^index$', htmlviews.IndexView,
        name='index'),
    url(r'^inkassosag$', inkassosag.InkassoSag.as_view(),
        name='inkassosag'),
    url(r'^rentenota$', rentenota.RenteNota.as_view(),
        name='rentenota (NY18)'),
]
