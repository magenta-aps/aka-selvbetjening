from akasite.rest.base import JSONRestView
from akasite.rest.prisme import Prisme
from django.http import HttpResponse
from django.core import files
from django.conf import settings
import requests
import tempfile
import os


class FileDownload(JSONRestView):
    def fetchFile(self, url, destfolder):
        '''
        Fetches a file from url, and stores it in destfolder with the name
        given as the last part of the url.
        I prefer this to the method using NamedTemporaryFile.
        '''

        request = requests.get(url, stream=True)

        if request.status_code != requests.codes.ok:
            return None

        file_name = url.split('/')[-1]
        destfile = destfolder + file_name
        with open(destfile, 'wb+') as destination:
            for block in request.iter_content(1024 * 8):
                if block:
                    destination.write(block)

        return destfile, file_name

    def initiatedownload(self, path, contenttype):
        with open(path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type=contenttype)
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
            return response

        return HttpResonseBadRequest

    def get(self, request, *args, **kwargs):
        '''
        This method expects '?f=url' in the request.
        It will then download the resource, store it locally
        and pass it on to the caller.

        How to get the url in real life?
        How to get the contenttype in real life
        '''

        prisme = Prisme()
        # url = prisme.receiveFromPrisme(None)
        url = request.GET.get('f', '')
        dummyresponse = {"serversays": "Hello. You said FileDownload/GET"}
        dummyresponse['url'] = url
        result = self.fetchFile(url, settings.MEDIA_URL)
        dummyresponse['localfilename'] = result[0]
        dummyresponse['origfilename'] = result[1]

        contenttype = 'application/pdf'  # How to get this in real life?
        return self.initiatedownload(result[0], contenttype)

