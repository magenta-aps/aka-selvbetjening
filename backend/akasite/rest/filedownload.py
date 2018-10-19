from akasite.rest.base import JSONRestView
from akasite.rest.prisme import Prisme
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.conf import settings
import os


class FileDownload(JSONRestView):
    def initiatedownload(self, path, contenttype):
        with open(path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type=contenttype)
            cd = 'inline; filename=' + os.path.basename(path)
            response['Content-Disposition'] = cd
            return response

        return HttpResponseBadRequest

    def get(self, request, *args, **kwargs):
        '''
        As a test, this method expects '?f=url' in the request.
        It will then download the resource, store it locally
        and pass it on to the caller.

        How to get the url in real life?
        How to get the contenttype in real life
        '''

        prisme = Prisme()
        # url = prisme.receiveFromPrisme(None)
        url = request.GET.get('f', '')
        filename = url.split('/')[-1]
        filefetched = prisme.fetchPrismeFile(url, settings.MEDIA_URL+filename)

        if filefetched:
            contenttype = 'application/pdf'  # How to get this in real life?
            return self.initiatedownload(settings.MEDIA_URL+filename,
                                         contenttype)
