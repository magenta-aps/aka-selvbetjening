Sphinx/autodoc:
For at benytte autodoc har jeg gjort følgende:
  I doc/conf.py skal sys.path sættes, så Sphinx kan se alle de directories
  hvor der ligger moduler. Jeg tilføjede disse 3:
  ../backend/akasite/rest
  ../backend/akasite
  ../backend

I en given rst-fil kan så tilføje disse direktiver, for at få Sphinx til at
tilføje modul-kode til docs:

.. automodule:: <modulnavn>  
   :members:
Mere info her:
http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

Jeg har selv til en start brugt denne syntax til klasser og metoder,
som Sphinx genkender:
    def postfile(self, request, *args, **kwargs):
        '''
        Base class for POST handler for file upload.
        We use multipart/formdata.
        Django places uploaded files in request.FILES.
        Additional form fields end up in request.POST.
        Moves any uploaded files in the directory settings.MEDIA_URL.
        Stores file metadata in self.payload['file'].
        Stores form fields in self.payload['POST'].
    
        :param request: The request.
        :type request: HttpRequest.
        :returns:  HttpResponse, HttpResponseBadRequest
        :raises: ContentTypeError, json.decoder.JSONDecodeError, IOError
        '''


