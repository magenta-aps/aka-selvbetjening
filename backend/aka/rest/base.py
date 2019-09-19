from django.views import View
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.conf import settings
import json
import os
import random
import logging

logger = logging.getLogger(__name__)


class ContentTypeError(Exception):
    """Exception raised for errors in the content-type
       of the request.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
