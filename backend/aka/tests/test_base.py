import json
import logging

from aka.utils import ErrorJsonResponse
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorDict, ErrorList
from django.test import SimpleTestCase


class BasicTestCase(SimpleTestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def checkReturnValIsJSON(self, response):
        try:
            charset = response.charset
            json.dumps(json.loads(response.content.decode(charset)), indent=4)
        except json.decoder.JSONDecodeError:
            self.fail('Did not get JSON back.')

