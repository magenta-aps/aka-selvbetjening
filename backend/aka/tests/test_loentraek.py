import logging
from datetime import date

from aka.clients.prisme import PrismePayrollRequest
from aka.clients.prisme import PrismePayrollRequestLine
from aka.clients.prisme import PrismePayrollResponse
from aka.tests.mixins import TestMixin
from django.core.files import File
from django.test import TestCase
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
