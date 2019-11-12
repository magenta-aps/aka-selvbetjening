import json
import logging

from aka.clients.prisme import PrismeImpairmentResponse
from aka.tests.mixins import SoapTestMixin
from django.test import SimpleTestCase
from lxml import etree


class BasicTestCase(SoapTestMixin, SimpleTestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.url = '/nedskrivning'
        self.service_mock = self.mock_soap('aka.clients.prisme.Prisme.process_service')
        self.service_mock.return_value = [
            PrismeImpairmentResponse(None, f"<CustCollClaimTableFuj><RecId>1234</RecId></CustCollClaimTableFuj>")
        ]
        self.cvrcheck_mock = self.mock_soap('aka.clients.prisme.Prisme.check_cvr')
        self.cvrcheck_mock.return_value = '12345678'  # claimant_id

    def test_validRequest1(self):
        # Contains just the required fields
        formData = {
            'debitor': 'test-debitor',
            'ekstern_sagsnummer': '1234',
            'beloeb': '100',
            'sekvensnummer': '1'
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'rec_id': 1234})


    def test_invalidRequest1(self):
        # Contains just the required fields
        formData = {
            'debitor': 'test-debitor',
            'ekstern_sagsnummer': '1234',
            'beloeb': 'aaa',
            'sekvensnummer': '1'
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        el = root.xpath("//div[@class='has-error']/input[@name='beloeb'][@value='aaa']")
        self.assertEqual(1, len(el))
