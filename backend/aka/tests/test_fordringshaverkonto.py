import json
import logging

from django.test import SimpleTestCase


# Create your tests here.
class BasicTestCase(SimpleTestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.url = '/fordringshaverkonto'

    def checkReturnValIsJSON(self, response):
        try:
            charset = response.charset
            return json.loads(response.content.decode(charset))
        except json.decoder.JSONDecodeError:
            self.fail('Did not get JSON back.')
