===========
REST API
===========

This directory contains documentation necessary to use the REST-interface exposed
by the backend.



.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :glob:

   api/*
   
   

CSRF-token is required for all endpoints.
Get the token initially from a GET-request to an endpoint [WHICH? /index? the view must use 'ensure_csrf_cookie' or similar]
Send the token as a header with key X-CSRFTOKEN.

Content-Type must be 'application/json' when not uploading files
and 'multipart/form-data' when uploading files, even when there is additional data.


Making requests
===============

/inkassosag
-----------

POST: Sends data to the server.

Data: Send serialised Form-Data in the body.

GET: Nothing to GET from this endpoint at the moment.


/rentenota
----------

GET: Get rentenota from Prisme. Requires from-date and to-date

POST: Not allowed here.

Notes
=====

Django and HTTP headers:
------------------------

Custom HTTP headers in DJANGO/WSGI are converted according to this rule (by Django):

HTTP_ is prepended, dashes are converted to underscores and the whole string is

converted to upper case.

Using Postman
-------------

When doing a POST in Postman, without any file upload, you set Content-Type and X-CSRFTOKEN under the headers tab.

When uploading files through POSTMAN, you do not set the Content-Type yourself, instead you choose
form-data in the body tab and choose 'File' in the key field in the table below)

    (In POSTMAN you do not set the Content-Type yourself, instead you choose
    form-data in the body tab and choose 'File' in the key field in the table below)

Getting responses
=================

The HTTP response should inform the frontend if the request was succesful or not. 
If the requested data elicits errors, the response should contain JSON with information regarding said errors::

    {
        "errors": [
            {
                "da": "PRISME er ikke tilgængelig i øjeblikket",
                "kl": "PRISME Illuquarnuulit annuueriset"
            },
            {
                "da": "Dette er den forkerte formular",
                "kl": "Illuquarnuulit annuuerisetaqaq"
            }
            
        ],
        "fielderrors": {
            "field_a": {
                "da": "Navnet må ikke indeholde disse tegn: @$%&*",
                "kl": "Illuquarnuulit annuueriset: @$%&*"
            },
            "field_b": {
                "da": "Dette felt er obligatorisk",
                "kl": "Illuquarnuulit annuueriset"
            },
            "field_c": {
                "da": "36 er for lavt et tal",
                "kl": "Illuquarnuulit 36 annuueriset"
            }
        }
    }

Error strings should be send in both Danish (da) and Greenlandic (kl).
