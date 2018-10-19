from django.conf.urls import url

from akasite.rest import inkassosag, fileupload, filedownload
from akasite import htmlviews

app_name = 'akasite'

urlpatterns = [
    url(r'^index$', htmlviews.IndexView.as_view(),
        name='index'),
    url(r'^indberetning$', htmlviews.Indberetning.as_view(),
        name='indberetning'),
    url(r'^inkassosag$', inkassosag.InkassoSag.as_view(),
        name='inkassosag'),
    url(r'^filupload$', fileupload.FileUpload.as_view(),
        name='filupload'),
    url(r'^rentenota$', filedownload.FileDownload.as_view(),
        name='rentenota (NY18)'),
]
