=======
Logging
=======


Python Logger
=============

Logging in python is quite simple:

.. code-block:: python
    
    # import the logging library
    import logging

    # Get an instance of a logger
    logger = logging.getLogger(__name__)

    def my_view(request, arg1, arg):
        ...
        if bad_mojo:
            # Log an error message
            logger.error('Something went wrong!')


Different logging lvls:

.. code-block:: python
    
    # comments are formatted as following:
    # NAME (numeric value) - extra text
    #
    # the higher the numeric value, the more important the log-message is, and 
    # the more handlers will write the log-message.

    # DEBUG (10)- Django only outputs this to the console, if debug is enabled.
    logger.debug(msg, *args, **kwargs)

    # INFO (20) - Information that a non-problematic event occured, eg a 
    # HTTP-request was made. 
    logger.info(msg, *args, **kwargs)

    # WARNING (30) - Information that could potentially be a problem, or evolve
    # into a problem later.
    logger.warning(msg, *args, **kwargs)

    # ERROR (40) - Information that an error occured. This should be used for errors
    # which poses a problem to a single request, or a single request type.
    logger.error(msg, *args, **kwargs)

    # CRITICAL (50) - Information that a critical error occured, this is an error
    # which poses a critical problem to a bigger part of users.
    logger.critical(msg, *args, **kwargs)
    






Further Refferences
===================

`Python Docs <https://docs.python.org/3.7/library/logging.html>`_

`Django Docs <https://docs.djangoproject.com/en/1.11/topics/logging/>`_


