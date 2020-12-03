CSRF
----

CSRF-token is required for all endpoints.
Get the token initially from a GET-request to an endpoint [WHICH? /index? the view must use 'ensure_csrf_cookie' or similar]
Send the token as a header with key X-CSRFTOKEN.

Responses
----------

In case of successful requests, the backend response is HTTP status 200. Only in case og GET requests will the body contain data.

In case of errors, the backend response is a JSON structure such as this, with information regarding
general as well as field specific errors::

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
        "fieldErrors": {
            "field_a": [{
                "da": "Navnet må ikke indeholde disse tegn: @$%&*",
                "kl": "Illuquarnuulit annuueriset: @$%&*"
            }],
            "field_b": [{
                "da": "Dette felt er obligatorisk",
                "kl": "Illuquarnuulit annuueriset"
            }],
            "field_c": [{
                "da": "36 er for lavt et tal",
                "kl": "Illuquarnuulit 36 annuueriset"
            }]
        }
    }

Error strings should be sent in both Danish (da) and Greenlandic (kl).

Using Postman to make requests
------------------------------

When doing a POST in Postman, without any file upload, you set Content-Type and X-CSRFTOKEN under the *headers* tab.

When uploading files through POSTMAN, you do not set the Content-Type yourself, instead you choose
form-data in the *body* tab and choose 'File' in the key field in the table below.
