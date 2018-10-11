REST API for AKA-selvbetjeningsløsninger
==============================================

The REST API is made using a class based view.

Base class is JSONRestView. This handles two forms of POST requests,
one with an ordinary data payload, and one with uploaded file(s).
The basic idea is to let the base class interact with Django's request object,
so that body and/or form fields are converted to JSON, and any files are moved
to the designated location, which is settings.MEDIA_URL

JSONRestView.post():
--------------------
  This method requires content-type to be 'application/json; charset=utf-8'.
  Handles 'ordinary' post request, and decodes data, according to charset,
  into self.payload.
  If all is well, returns an empty HttpResponse, (i.e. status 200).
  If content-type/charset is not as required, this method returns an
  HttpResponseBadRequest (i.e. status = 400).

JSONRestView.postfile():
------------------------
  This method handles file(s) uploaded in a well-known way, and requires 
  content-type to be 'multipart/form-data'. This makes it easy to do in Django as
  well as in Vue and other frontend tools.
  At the moment, I am not sure how, if at all, we can handle charset for the file(s).
  See https://tools.ietf.org/html/rfc7578 for more.
  If content-type is not as required, this method returns an
  HttpResponseBadRequest (i.e. status = 400).


NB: Make sure to use this decorator on any sub class of JSONRestView, 
if you want it protected from CSRF:
@method_decorator(ensure_csrf_cookie, name='dispatch')
