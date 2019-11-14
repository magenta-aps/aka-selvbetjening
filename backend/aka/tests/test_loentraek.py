import logging
from datetime import date

from aka.clients.prisme import PrismePayrollRequest
from aka.clients.prisme import PrismePayrollRequestLine
from aka.clients.prisme import PrismePayrollResponse
from aka.tests.mixins import TestMixin
from django.core.files import File
from django.test import TestCase
from lxml import etree
from xmltodict import parse as xml_to_dict


class BasicTestCase(TestMixin, TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.url = '/loentraek'
        self.service_mock = self.mock_soap('aka.clients.prisme.Prisme.process_service')
        self.service_mock.return_value = [
            PrismePayrollResponse(None, f"<CustPayrollFromEmployerHeaderFUJ><RecId>1234</RecId></CustPayrollFromEmployerHeaderFUJ>")
        ]


    ### PRISME INTERFACE TESTS ###

    def test_create_payroll_request_parse(self):
        attachment = File(open('aka/tests/resources/testfile.pdf'))
        attachment.close()
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

    ### POSITIVE TESTS

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
