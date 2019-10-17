import json
import logging

from django.test import Client, override_settings
from django.test import TestCase


@override_settings(OPENID_CONNECT={'enabled': False})
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
    #
    # # Dates OK, invalid cvr
    def test_Get_1(self):
        for y in range(2000, 2019):
            for m in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
                response = self.c.get(self.url + f'/{y}/{m}')
        self.assertEqual(response.status_code, 403)
        self.checkReturnValIsJSON(response)
