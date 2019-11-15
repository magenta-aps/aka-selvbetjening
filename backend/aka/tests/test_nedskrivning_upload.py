import json
import logging

from aka.clients.prisme import PrismeImpairmentRequest, PrismeImpairmentResponse
from aka.tests.mixins import TestMixin
from django.core.files import File
from django.test import TestCase
from lxml import etree
from xmltodict import parse as xml_to_dict


class BasicTestCase(TestMixin, TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.url = '/nedskrivning/upload'
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

    def test_impairment_success(self):
        with File(open('aka/tests/resources/impairment.csv', 'rb')) as file:
            formData = {
                'file': file
            }
            response = self.client.post(self.url, formData)
            self.assertEqual(response.status_code, 200)
            root = etree.fromstring(response.content, etree.HTMLParser())
            el = root.xpath("//ul[@class='success-list']/li")
            self.assertEqual(1, len(el))
            self.assertEqual('1234', el[0].text)


    ### NEGATIVE TESTS ###

    def test_impairment_empty_csv(self):
        with File(open('aka/tests/resources/impairment_empty.csv', 'rb')) as file:
            formData = {
                'file': file
            }
            response = self.client.post(self.url, formData)
            self.assertEqual(response.status_code, 200)
            root = etree.fromstring(response.content, etree.HTMLParser())
            erroritems = root.xpath("//div[@data-field='id_file']//ul[@class='errorlist']/li")
            self.assertEqual(1, len(erroritems))
            self.assertEqual('common.upload.empty', erroritems[0].attrib.get('data-trans'))


    def test_impairment_missing_amount(self):
        with File(open('aka/tests/resources/impairment_missing.csv', 'rb')) as file:
            formData = {
                'file': file
            }
            response = self.client.post(self.url, formData)
            self.assertEqual(response.status_code, 200)
            root = etree.fromstring(response.content, etree.HTMLParser())
            print(response.content)
            erroritems = root.xpath("//div[@data-field='id_file']//ul[@class='errorlist']/li")
            self.assertEqual(2, len(erroritems))
            self.assertEqual('common.upload.validation_item', erroritems[0].attrib.get('data-trans'))
            self.assertEqual('common.upload.validation_item', erroritems[1].attrib.get('data-trans'))
