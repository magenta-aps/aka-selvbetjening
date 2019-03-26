from urllib.parse import urlencode
from django.test import TestCase
from django.test import Client
from django.urls import reverse
import httpretty
from django.conf import settings
import json

import os


class BasicTestCase(TestCase):

    def setUp(self):
        httpretty.enable()
        httpretty.register_uri(
            uri=settings.OPENID_CONNECT['authorization_endpoint'],
            method=httpretty.GET,
            body='ok',
        )
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'openid-configuration.json')) as configuration:
            httpretty.register_uri(uri='https://loginqa.sullissivik.gl/.well-known/openid-configuration',
                                   method=httpretty.GET,
                                   body=json.dumps(json.load(configuration)))
        json_response = {
            "access_token": "SlAV32hkKG",
            "token_type": "Bearer",
            "id_token": ("eyJhbGciOiJSUzI1NiIsImtpZCI6IjFlOWdkazcifQ.ewogImlzc"
            "yI6ICJodHRwOi8vc2VydmVyLmV4YW1wbGUuY29tIiwKICJzdWIiOiAiMjQ4Mjg5"
            "NzYxMDAxIiwKICJhdWQiOiAiczZCaGRSa3F0MyIsCiAibm9uY2UiOiAibi0wUzZ"
            "fV3pBMk1qIiwKICJleHAiOiAxMzExMjgxOTcwLAogImlhdCI6IDEzMTEyODA5Nz"
            "AKfQ.ggW8hZ1EuVLuxNuuIJKX_V8a_OMXzR0EHR9R6jgdqrOOF4daGU96Sr_P6q"
            "Jp6IcmD3HP99Obi1PRs-cwh3LO-p146waJ8IhehcwL7F09JdijmBqkvPeB2T9CJ"
            "NqeGpe-gccMg4vfKjkM8FcGvnzZUN4_KSP0aAp1tOJ1zZwgjxqGByKHiOtX7Tpd"
            "QyHE5lcMiKPXfEIQILVq0pc_E2DzL7emopWoaoZTF_m0_N0YzFC6g6EJbOEoRoS"
            "K5hoDalrcvRYLSrQAZZKflyuVCyixEoV9GfNQC3_osjzw2PAithfubEEBLuVVk4"
            "XUVrWOLrLl0nx7RkKU8NXNHq-rvKMzqg")
        }

        httpretty.register_uri(
            uri='https://loginqa.sullissivik.gl/connect/token',
            method=httpretty.POST,
            body=json.dumps(json_response),
            forcing_headers={'Content-Type': 'application/json'}
        )
        self.client = Client()

    def test_oauth_flow(self):
        # start oauth flow
        response = self.client.get(reverse('openid:login'))
        #self.assertRedirects(response)
        print(response)

        print(self.client.session.keys())  # contains oid_state and oid_nonce



        params = {
            'state': self.client.session['oid_state'],
            'code': '1234'
        }
        query = urlencode(params, 'utf-8')

        # simulate callback
        response = self.client.get('{url}?{query}'.format(url=reverse('openid:callback'), query=query))
        print(response)

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()