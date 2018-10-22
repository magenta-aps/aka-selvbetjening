from akasite.rest.base import JSONRestView
from akasite.rest.prisme import Prisme
from akasite.rest.utils import AKAUtils
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.conf import settings
import os
import json


class RenteNota(JSONRestView):
    def initiatedownload(self, path, contenttype):
        with open(path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type=contenttype)
            cd = 'inline; filename=' + os.path.basename(path)
            response['Content-Disposition'] = cd
            return response

        return HttpResponseBadRequest

    def fetch(self, request, *args, **kwargs):
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

    def get(self, request, *args, **kwargs):
        '''
        Get rentenota data for the given interval.
        '''

        fromdate = request.GET.get('fromdate', '')
        todate = request.GET.get('todate', '')
        prisme = Prisme()
        data = prisme.getRentenota(fromdate, todate)
        return HttpResponse(json.dumps(data), content_type=JSONRestView.CT1)


    def post(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['GET'])
