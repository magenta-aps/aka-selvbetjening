from django.test import TestCase
from django.test import Client
import json

# Create your tests here.
class BasicTestCase(TestCase):
    def setUp(self):
        print("Now in setup...")
        self.c = Client()
        self.url = '/aka/v1/inkassosag/'

    def test_Get(self):
        response1 = self.c.get(self.url)
        self.assertEqual(response1.status_code, 200)

    # Legal JSON in body.
    def test_Post_1(self):
        jsondata =  '{"sagsnummer": "789321", "fornavn": "karl"}'
        response1 = self.c.post(self.url, content_type='application/json; charset=utf-8', data=jsondata)
        self.assertEqual(response1.status_code, 200)

    # Illegal JSON in body.
    def test_Post_2(self):
        jsondata =  '{: "karl"}'
        response1 = self.c.post(self.url, content_type='application/json; charset=utf-8', data=jsondata)
        self.assertEqual(response1.status_code, 400)

    # Empty JSON in body.
    def test_Post_3(self):
        jsondata =  ''
        response1 = self.c.post(self.url, content_type='application/json; charset=utf-8', data=jsondata)
        self.assertEqual(response1.status_code, 400)

    # Send data as default, i.e. multipart. Should also fail, as body will be empty.
    def test_Post_4(self):
        response1 = self.c.post(self.url, {'username': 'john', 'password': 'smith'})
        self.assertEqual(response1.status_code, 400)

