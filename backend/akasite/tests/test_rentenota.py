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

    # Dates OK, good request and 200 return.
    def test_Get_1(self):
        response = self.c.get(self.url + '/from2018-01-01to2018-01-31')
        self.assertEqual(response.status_code, 200)
        self.checkReturnValIsJSON(response)

    # Error in to-date. Returns 400, bad request.
    def test_Get_2(self):
        response = self.c.get(self.url + '/from2018-01-01to2018-00-31')
        self.assertEqual(response.status_code, 400)
        self.checkReturnValIsJSON(response)

    # Error in to-date. Returns 400, bad request.
    def test_Get_3(self):
        response = self.c.get(self.url + '/from2018-05-09to2018-05-01')
        self.assertEqual(response.status_code, 400)
        self.checkReturnValIsJSON(response)

    # From and to are correct, but method not allowed.
    def test_Post_1(self):
        ctstring = 'application/json; charset=utf-8'
        response = self.c.post(self.url + '/from2018-01-01to2018-01-31',
                               content_type=ctstring, data='')
        self.assertEqual(response.status_code, 405)

    # From and to are correct, without content-type and data,
    # but method not allowed.
    def test_Post_2(self):
        response = self.c.post(self.url + '/from2018-01-01to2018-01-31')
        self.assertEqual(response.status_code, 405)

    # To-date incorrect, so no match in URL dispatcher.
    def test_Post_3(self):
        response = self.c.post(self.url + '/from2018-01-01to2018-0-13')
        self.assertEqual(response.status_code, 404)
