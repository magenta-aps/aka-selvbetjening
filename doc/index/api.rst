===========
REST API
===========

This directory contains documentation necessary to use the REST-interface exposed
by the backend, without going too much in deatil with the actual implementations.



.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :glob:

   api/*
   
   

CSRF-token is required for all endpoints.

Get the token initially from a GET-request to an endpoint [WHICH? /index? the view must use 'ensure_csrf_cookie' or similar]

Making requests
===============

/inkassosag
-----------

POST: Sends data to the server.

Required headers:

    Content-Type = 'application/json'

    X-CSRFTOKEN = the value from the relevant cookie, set by the server.

Data: Send serialised JSON in the body.

GET: Nothing to GET from this endpoint at the moment.


/filupload
----------

POST: Send file(s) and possibly other form fields to the server.

Required headers:

    X-CSRFTOKEN = the value from the relevant cookie, set by the server.

    Content-Type = multipart/form-data

/rentenota
----------

GET: Get rentenota from Prisme. Requires from-date and to-date


Note on using Postman
=====================

When doing a POST in Postman, without any file upload, you set Content-Type and X-CSRFTOKEN under the headers tab.

When uploading files through POSTMAN, you do not set the Content-Type yourself, instead you choose
form-data in the body tab and choose 'File' in the key field in the table below)

