import json
import logging

from aka.clients.prisme import PrismeImpairmentRequest, PrismeImpairmentResponse
from aka.tests.mixins import TestMixin
from django.test import TestCase
from lxml import etree
from xmltodict import parse as xml_to_dict


class BasicTestCase(TestMixin, TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.url = '/nedskrivning'
        self.service_mock = self.mock_soap('aka.clients.prisme.Prisme.process_service')
        self.service_mock.return_value = [
            PrismeImpairmentResponse(None, f"<CustCollClaimTableFuj><RecId>1234</RecId></CustCollClaimTableFuj>")
        ]
        self.cvrcheck_mock = self.mock_soap('aka.clients.prisme.Prisme.check_cvr')
        self.cvrcheck_mock.return_value = '12345678'  # claimant_id
        session = self.client.session
        session['user_info'] = {'CVR': '12479182'}  # 12479182
        session.save()


### PRISME INTERFACE TESTS ###

    def test_impairment_request_parse(self):
        request = PrismeImpairmentRequest('32SE', '12345678', 'ref123', -100.5, 'AKI-000047')
        self.compare(
            xml_to_dict(self.get_file_contents('aka/tests/resources/impairment_request.xml')),
            xml_to_dict(request.xml),
            ""
        )

    def test_impairment_response_parse(self):
        response = PrismeImpairmentResponse(None, self.get_file_contents('aka/tests/resources/impairment_response.xml'))
        self.assertEqual("5637238342", response.rec_id)


    ### POSITIVE TESTS ###

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
        root = etree.fromstring(response.content, etree.HTMLParser())
        el = root.xpath("//ul[@class='success-list']/li")
        self.assertEqual(1, len(el))
        self.assertEqual('1234', el[0].text)


    ### NEGATIVE TESTS ###

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
