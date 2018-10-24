from django.test import TestCase
from django.test import Client
import json
import logging


# Create your tests here.
class BasicTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.c = Client()
        self.url = '/inkassosag'

    def checkReturnValIsJSON(self, response):
        try:
            charset = response.charset
            json.dumps(json.loads(response.content.decode(charset)), indent=4)
        except json.decoder.JSONDecodeError:
            self.fail('Did not get JSON back.')

    def test_Get(self):
        response = self.c.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.checkReturnValIsJSON(response)

    # Legal JSON in body, and legal content_type.
    def test_Post_1(self):
        jsondata = '{"sagsnummer": "789321", "fornavn": "karl"}'
        ctstring = 'application/json; charset=utf-8'
        response = self.c.post(self.url, content_type=ctstring, data=jsondata)
        self.assertEqual(response.status_code, 200)
        self.checkReturnValIsJSON(response)

    # Illegal JSON in body.
    def test_Post_2(self):
        jsondata = '{: "karl"}'
        ctstring = 'application/json; charset=utf-8'
        response = self.c.post(self.url, content_type=ctstring, data=jsondata)
        self.assertEqual(response.status_code, 400)
        self.checkReturnValIsJSON(response)

    # Empty JSON in body, legal content-type.
    # For some reason, the server cannot find content-type in the request,
    # so this fails, but for an unexpected reason.
    def test_Post_3(self):
        jsondata = ''
        ctstring = 'application/json; charset=utf-8'
        response = self.c.post(self.url, content_type=ctstring, data=jsondata)
        self.assertEqual(response.status_code, 400)
        self.checkReturnValIsJSON(response)

    # Send data as multipart. Should not fail, we accept data in raw body.
    def test_Post_4(self):
        response = self.c.post(self.url, {'name': 'john', 'password': 'xy'})
        self.assertEqual(response.status_code, 200)
        self.checkReturnValIsJSON(response)

    # Empty charset. Should fail.
    def test_Post_5(self):
        jsondata = '{"name" : "karl"}'
        ctstring = 'application/json; charset='
        response = self.c.post(self.url, content_type=ctstring, data=jsondata)
        self.assertEqual(response.status_code, 400)
        self.checkReturnValIsJSON(response)

    # No charset. Should fail.
    def test_Post_6(self):
        jsondata = '{"name" : "karl"}'
        ctstring = 'application/json'
        response = self.c.post(self.url, content_type=ctstring, data=jsondata)
        self.assertEqual(response.status_code, 400)
        self.checkReturnValIsJSON(response)

    # Incorrect content-type, should fail.
    def test_Post_7(self):
        jsondata = '{"name" : "karl"}'
        ctstring = 'text/plain; charset=utf-8'
        response = self.c.post(self.url, content_type=ctstring, data=jsondata)
        self.assertEqual(response.status_code, 400)
        self.checkReturnValIsJSON(response)

    # Other charset. Should not fail.
    def test_Post_8(self):
        jsondata = '{"name" : "karl"}'
        ctstring = 'application/json; charset=iso8859-1'
        response = self.c.post(self.url, content_type=ctstring, data=jsondata)
        self.assertEqual(response.status_code, 200)
        self.checkReturnValIsJSON(response)

    def test_Schema(self):
        response = self.c.get(self.url + '/schema')
        self.assertEqual(response.status_code, 200)
        self.checkReturnValIsJSON(response)
