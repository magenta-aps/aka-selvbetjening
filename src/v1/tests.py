from django.test import TestCase
from django.test import Client
import json

# Create your tests here.
class BasicTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.url = '/aka/v1/inkassosag/'
        self.url2 = '/aka/v1/debitor/'

    def test_Get(self):
        response1 = self.c.get(self.url)
        self.assertEqual(response1.status_code, 200)
        print(response1.content.decode('utf-8'))

    # Legal JSON in body.
    def test_Post_1(self):
        jsondata =  '{"sagsnummer": "789321", "fornavn": "karl"}'
        response1 = self.c.post(self.url, content_type='application/json; charset=utf-8', data=jsondata)
        self.assertEqual(response1.status_code, 200)
        try:
            content = json.loads(response1.content.decode('utf-8'))
            print(json.dumps(content))
        except:
            content = response1.content.decode('utf-8')
            self.fail('JSON error. content=' + content)

    # Illegal JSON in body.
    def test_Post_2(self):
        jsondata =  '{: "karl"}'
        response1 = self.c.post(self.url, content_type='application/json; charset=utf-8', data=jsondata)
        self.assertEqual(response1.status_code, 400)
        print(response1.content.decode('utf-8'))

    # Empty JSON in body.
    # For some reason, the server cannot find content-type in the request, so this fails,
    # but for an unexpected reason.
    def test_Post_3(self):
        try:
            jsondata = ''
            response1 = self.c.post(self.url, content_type='application/json; charset=utf-8', data=jsondata)
            self.assertEqual(response1.status_code, 400)
            print(response1.content.decode('utf-8'))
        except:
            content = response1.content.decode('utf-8')
            self.fail('JSON error. content=' + content)

    # Send data as default, i.e. multipart. Should also fail, as body will be empty.
    def test_Post_4(self):
        response1 = self.c.post(self.url, {'username': 'john', 'password': 'smith'})
        self.assertEqual(response1.status_code, 400)
        print(response1.content.decode('utf-8'))

    # Empty charset. Should fail.
    def test_Post_5(self):
        jsondata =  '{"name" : "karl"}'
        response1 = self.c.post(self.url, content_type='application/json; charset=', data=jsondata)
        self.assertEqual(response1.status_code, 400)
        print(response1.content.decode('utf-8'))

    # No charset. Should fail.
    def test_Post_6(self):
        jsondata =  '{"name" : "karl"}'
        response1 = self.c.post(self.url, content_type='application/json', data=jsondata)
        self.assertEqual(response1.status_code, 400)
        print(response1.content.decode('utf-8'))

    # Other charset. Should not fail.
    def test_Post_7(self):
        jsondata =  '{"name" : "karl"}'
        response1 = self.c.post(self.url, content_type='application/json; charset=iso8859-1', data=jsondata)
        self.assertEqual(response1.status_code, 200)
        print(response1.content.decode('utf-8'))

    # ---------- DEBITOR -------------
    def test_Get_Debitor(self):
        response1 = self.c.get(self.url2)
        self.assertEqual(response1.status_code, 200)
        print(response1.content.decode('utf-8'))

    # Legal JSON in body.
    def test_Post1debitor(self):
        jsondata =  '{"sagsnummer": "789321", "fornavn": "karl"}'
        response1 = self.c.post(self.url2, content_type='application/json; charset=utf-8', data=jsondata)
        self.assertEqual(response1.status_code, 200)
        try:
            content = json.loads(response1.content.decode('utf-8'))
            print(json.dumps(content))
        except:
            content = response1.content.decode('utf-8')
            self.fail('JSON error. content=' + content)
            print('JSON error. content=' + content)
