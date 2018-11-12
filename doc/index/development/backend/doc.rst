REST API for AKA-selvbetjeningsløsninger
==============================================

The REST API is made using a class based view.

Base class is JSONRestView, and the individual user endpoints,
i.e. inkassosag, rentenota etc., have a subclass each.

**Django and HTTP headers**

Custom HTTP headers in DJANGO/WSGI are converted according to this rule (by Django):

**HTTP_** is prepended, dashes are converted to underscores and the whole string is converted to upper case.

Code listings
-------------

.. automodule:: base
   :members:

.. automodule:: inkassosag
   :members:

.. automodule:: prisme
   :members:

.. automodule:: rentenota
   :members:

.. automodule:: utils
   :members:

.. automodule:: validation
   :members:

.. automodule:: sharedfiles
   :members:
