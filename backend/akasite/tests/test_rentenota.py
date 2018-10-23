from django.test import TestCase
from django.test import Client
import json
import logging


# Create your tests here.
class BasicTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.c = Client()
        self.url = '/rentenota'

    def checkReturnValIsJSON(self, response):
        try:
            charset = response.charset
            json.dumps(json.loads(response.content.decode(charset)), indent=4)
        except json.decoder.JSONDecodeError:
            self.fail('Did not get JSON back.')

    def test_Get(self):
        response = self.c.get(self.url + '?fromdate=20180101&todate=20180131')
        self.assertEqual(response.status_code, 200)
        self.checkReturnValIsJSON(response)

    def test_Post(self):
        ctstring = 'application/json; charset=utf-8'
        response = self.c.post(self.url + '?fromdate=20180101&todate=20180131',
                               content_type=ctstring, data='')
        self.assertEqual(response.status_code, 405)
