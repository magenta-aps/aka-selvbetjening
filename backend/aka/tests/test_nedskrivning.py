import logging

from aka.clients.prisme import PrismeImpairmentRequest, PrismeImpairmentResponse
from aka.tests.mixins import TestMixin
from django.test import TestCase
from lxml import etree
from xmltodict import parse as xml_to_dict


class BasicTestCase(TestMixin, TestCase):

    def setUp(self):
        super(BasicTestCase, self).setUp()
        logging.disable(logging.CRITICAL)
        self.url = '/nedskrivning'


class RemoteTestCase(BasicTestCase):
    pass
    # def test_impairment_success(self):
    #     session = self.client.session
    #     session['user_info'] = {'CVR': '19785289'}
    #     session.save()
    #     try:
    #         formData = {
    #             'debitor': 'test-debitor',
    #             'ekstern_sagsnummer': '1234',
    #             'beloeb': '100',
    #             'sekvensnummer': '1'
    #         }
    #         response = self.client.post(self.url, formData)
    #         self.assertEqual(response.status_code, 200)
    #         root = etree.fromstring(response.content, etree.HTMLParser())
    #         el = root.xpath("//ul[@class='success-list']/li")
    #         self.assertEqual(1, len(el))
    #         self.assertEqual('1234', el[0].text)
    #     except ConnectionError:
    #         print("\nRemote test: Cannot connect to remote service")

    #
    # def test_invalid_cvr(self):
    #     session = self.client.session
    #     session['user_info'] = {'CVR': '12345678'}
    #     session.save()
    #     try:
    #         formData = {
    #             'debitor': 'test-debitor',
    #             'ekstern_sagsnummer': '1234',
    #             'beloeb': '100',
    #             'sekvensnummer': '1'
    #         }
    #         response = self.client.post(self.url, formData)
    #         self.assertEqual(response.status_code, 200)
    #         root = etree.fromstring(response.content, etree.HTMLParser())
    #         el = root.xpath("//h1[@class='page-header']")
    #         self.assertEqual(1, len(el))
    #         self.assertEqual('common.error.access_denied', el[0].attrib.get('data-trans'))
    #     except ConnectionError:
    #         print("\nRemote test: Cannot connect to remote service")


class LocalTestCase(BasicTestCase):

    def setUp(self):
        super(LocalTestCase, self).setUp()
        session = self.client.session
        session['user_info'] = {'CVR': '12479182'}
        session.save()
        self.prisme_return = {
            'PrismeImpairmentRequest': PrismeImpairmentResponse(None, "<CustCollClaimTableFuj><RecId>1234</RecId></CustCollClaimTableFuj>")
        }

    # PRISME INTERFACE TESTS

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

    # POSITIVE TESTS

    def test_impairment_success(self):
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

    # NEGATIVE TESTS

    def test_impairment_invalid_amount(self):
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
        erroritems = root.xpath("//div[@data-field='id_beloeb']//ul[@class='errorlist']/li")
        self.assertEqual(1, len(erroritems))
        self.assertEqual('invalid', erroritems[0].attrib.get('data-trans'))

    def test_impairment_missing_amount(self):
        # Contains just the required fields
        formData = {
            'debitor': 'test-debitor',
            'ekstern_sagsnummer': '1234',
            'sekvensnummer': '1'
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        erroritems = root.xpath("//div[@data-field='id_beloeb']//ul[@class='errorlist']/li")
        self.assertEqual(1, len(erroritems))
        self.assertEqual('error.required', erroritems[0].attrib.get('data-trans'))

    def test_impairment_missing_debitor(self):
        # Contains just the required fields
        formData = {
            'beloeb': 123,
            'ekstern_sagsnummer': '1234',
            'sekvensnummer': '1'
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        erroritems = root.xpath("//div[@data-field='id_debitor']//ul[@class='errorlist']/li")
        self.assertEqual(1, len(erroritems))
        self.assertEqual('error.required', erroritems[0].attrib.get('data-trans'))

    def test_impairment_missing_casenumber(self):
        # Contains just the required fields
        formData = {
            'debitor': 'test-debitor',
            'beloeb': 123,
            'sekvensnummer': '1'
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        erroritems = root.xpath("//div[@data-field='id_ekstern_sagsnummer']//ul[@class='errorlist']/li")
        self.assertEqual(1, len(erroritems))
        self.assertEqual('error.required', erroritems[0].attrib.get('data-trans'))

    def test_impairment_missing_sequencenumber(self):
        # Contains just the required fields
        formData = {
            'debitor': 'test-debitor',
            'beloeb': 123,
            'ekstern_sagsnummer': '1234',
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        erroritems = root.xpath("//div[@data-field='id_sekvensnummer']//ul[@class='errorlist']/li")
        self.assertEqual(1, len(erroritems))
        self.assertEqual('error.required', erroritems[0].attrib.get('data-trans'))
