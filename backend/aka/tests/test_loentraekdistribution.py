from django.test import TestCase, Client
import unittest
import json
import logging


# Create your tests here.
class BasicTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.c = Client()
        self.url = '/loentraekdistribution'

    def checkReturnValIsJSON(self, response):
        try:
            charset = response.charset
            return json.loads(response.content.decode(charset))
        except json.decoder.JSONDecodeError:
            self.fail('Did not get JSON back.')

    def test_validRequest1(self):
        response = self.c.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.checkReturnValIsJSON(response)

    def test_invalidRequest1(self):
        response = self.c.post(self.url)
        self.assertEqual(response.status_code, 405)
