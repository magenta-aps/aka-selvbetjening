import logging
from datetime import date

from aka.clients.prisme import PrismePayrollRequest
from aka.clients.prisme import PrismePayrollRequestLine
from aka.clients.prisme import PrismePayrollResponse
from aka.tests.mixins import TestMixin
from django.test import TestCase
from lxml import etree
from xmltodict import parse as xml_to_dict


class BasicTestCase(TestMixin, TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.url = '/loentraek'
        self.service_mock = self.mock('aka.clients.prisme.Prisme.process_service')
        self.service_mock.return_value = [
            PrismePayrollResponse(
                None,
                "<CustPayrollFromEmployerHeaderFUJ><RecId>1234</RecId></CustPayrollFromEmployerHeaderFUJ>"
            )
        ]
        session = self.client.session
        session['user_info'] = {'CVR': '12479182'}
        session.save()

    # PRISME INTERFACE TESTS

    def test_create_payroll_request_parse(self):
        request = PrismePayrollRequest(
            '10147573',
            date(2019, 11, 1),
            date(2019, 11, 1),
            100.5,
            [
                PrismePayrollRequestLine('1509551673', '00000001', 100, 25000),
                PrismePayrollRequestLine('2411803697', '00000001', 0.5, 25000),
            ]
        )
        self.compare(
            xml_to_dict(self.get_file_contents('aka/tests/resources/payroll_request.xml')),
            xml_to_dict(request.xml),
            ""
        )

    def test_create_payroll_response_parse(self):
        response = PrismePayrollResponse(None, self.get_file_contents('aka/tests/resources/payroll_response.xml'))
        self.assertEqual("5637238342", response.rec_id)

    # POSITIVE TESTS

    def test_payroll_success(self):
        # Contains just the required fields
        formData = {
            'year': 2019,
            'month': 11,
            'total_amount': '1000',
            'form-0-cpr': '1234567890',
            'form-0-agreement_number': '1',
            'form-0-amount': 200,
            'form-0-net_salary': 40000,
            'form-1-cpr': '1234567891',
            'form-1-agreement_number': '2',
            'form-1-amount': 200,
            'form-1-net_salary': 40000,
            'form-2-cpr': '1234567891',
            'form-2-agreement_number': '3',
            'form-2-amount': 200,
            'form-2-net_salary': 40000,
            'form-3-cpr': '1234567891',
            'form-3-agreement_number': '4',
            'form-3-amount': 400,
            'form-3-net_salary': 40000,
            'form-TOTAL_FORMS': 4,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        el = root.xpath("//ul[@class='success-list']/li")
        self.assertEqual(1, len(el))
        self.assertEqual('1234', el[0].text)

    # NEGATIVE TESTS

    def test_payroll_failure_missing_year(self):
        formData = {
            'month': 11,
            'total_amount': 200,
            'form-0-cpr': '1234567890',
            'form-0-agreement_number': '1',
            'form-0-amount': 200,
            'form-0-net_salary': 40000,
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        erroritems = root.xpath("//div[@data-field='id_year']//ul[@class='errorlist']/li")
        self.assertEqual(1, len(erroritems))
        self.assertEqual('error.required', erroritems[0].attrib.get('data-trans'))

    def test_payroll_failure_mmissing_month(self):
        formData = {
            'year': 2019,
            'total_amount': 200,
            'form-0-agreement_number': '1',
            'form-0-amount': 200,
            'form-0-net_salary': 40000,
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        erroritems = root.xpath("//div[@data-field='id_month']//ul[@class='errorlist']/li")
        self.assertEqual(1, len(erroritems))
        self.assertEqual('error.required', erroritems[0].attrib.get('data-trans'))

    def test_payroll_failure_missing_total_amount(self):
        formData = {
            'year': 2019,
            'month': 11,
            'form-0-cpr': '1234567890',
            'form-0-agreement_number': '1',
            'form-0-amount': 200,
            'form-0-net_salary': 40000,
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        erroritems = root.xpath("//div[@data-field='id_total_amount']//ul[@class='errorlist']/li")
        self.assertEqual(1, len(erroritems))
        self.assertEqual('error.required', erroritems[0].attrib.get('data-trans'))

    def test_payroll_failure_missing_cpr(self):
        formData = {
            'year': 2019,
            'month': 11,
            'total_amount': 200,
            'form-0-agreement_number': '1',
            'form-0-amount': 200,
            'form-0-net_salary': 40000,
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        erroritems = root.xpath("//div[@data-field='id_form-0-cpr']//ul[@class='errorlist']/li")
        self.assertEqual(1, len(erroritems))
        self.assertEqual('error.required', erroritems[0].attrib.get('data-trans'))

    def test_payroll_failure_missing_agreement_number(self):
        formData = {
            'year': 2019,
            'month': 11,
            'total_amount': 200,
            'form-0-cpr': '1234567890',
            'form-0-amount': 1000,
            'form-0-net_salary': 40000,
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        erroritems = root.xpath("//div[@data-field='id_form-0-agreement_number']//ul[@class='errorlist']/li")
        self.assertEqual(1, len(erroritems))
        self.assertEqual('error.required', erroritems[0].attrib.get('data-trans'))

    def test_payroll_failure_missing_amount(self):
        formData = {
            'year': 2019,
            'month': 11,
            'total_amount': 200,
            'form-0-cpr': '1234567890',
            'form-0-agreement_number': '1',
            'form-0-net_salary': 40000,
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        erroritems = root.xpath("//div[@data-field='id_form-0-amount']//ul[@class='errorlist']/li")
        self.assertEqual(1, len(erroritems))
        self.assertEqual('error.required', erroritems[0].attrib.get('data-trans'))

    def test_payroll_failure_sum_mismatch(self):
        formData = {
            'year': 2019,
            'month': 11,
            'total_amount': '1000',
            'form-0-cpr': '1234567890',
            'form-0-agreement_number': '1',
            'form-0-amount': 200,
            'form-0-net_salary': 40000,
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        erroritems = root.xpath("//div[@data-field='id_total_amount']//ul[@class='errorlist']/li")
        self.assertEqual(1, len(erroritems))
        self.assertEqual('loentraek.sum_mismatch', erroritems[0].attrib.get('data-trans'))
