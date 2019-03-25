from urllib.parse import urlencode

from django.test import TestCase
from django.test import Client
from django.urls import reverse


class BasicTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_something(self):
        response = self.client.get(reverse('openid:login'))
        #self.assertRedirects(response)
        print(response)
        print(self.client.session) # contains oid_state and oid_nonce
        params = {
            'state': self.client.session['oid_state'],
            'code': '1234'
        }
        query = urlencode(params, 'utf-8')

        response = self.client.get('{url}?{query}'.format(url=reverse('openid:callback'), query=query))
        print(response)