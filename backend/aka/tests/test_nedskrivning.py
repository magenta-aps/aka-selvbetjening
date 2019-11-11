import logging
import json

from django.test import SimpleTestCase

from aka.clients.prisme import PrismeImpairmentRequest


class BasicTestCase(SimpleTestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.url = '/nedskrivning'

def test_validRequest1(self):
    # Contains just the required fields
    self.mock.return_value = [PrismeImpairmentRequest(f"<CustCollClaimTableFuj><RecId>1234</RecId></CustCollClaimTableFuj>")]
    formData = {
        'debitor': 'test-debitor',
        'ekstern_sagsnummer': '1234',
        'beloeb': '100',
        'sekvensnummer': '1'
    }
    response = self.client.post(self.url, formData)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(json.loads(response.content), {'rec_id': 1234})

