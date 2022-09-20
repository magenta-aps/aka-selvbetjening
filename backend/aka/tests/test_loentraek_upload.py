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
        super(BasicTestCase, self).setUp()
        logging.disable(logging.CRITICAL)
        self.url = "/loentraek/upload/"
        session = self.client.session
        session["user_info"] = {"cvr": "12479182"}
        session.save()
        self.prisme_return = {
            "PrismePayrollRequest": PrismePayrollResponse(
                None,
                "<CustPayrollFromEmployerHeaderFUJ><RecId>1234</RecId></CustPayrollFromEmployerHeaderFUJ>",
            )
        }

    # PRISME INTERFACE TESTS

    def test_create_payroll_request_parse(self):
        attachment = File(open("aka/tests/resources/testfile.pdf"))
        attachment.close()
        request = PrismePayrollRequest(
            "10147573",
            date(2019, 11, 1),
            date(2019, 11, 1),
            100.5,
            [
                PrismePayrollRequestLine("1509551673", "00000001", 100, 25000),
                PrismePayrollRequestLine("2411803697", "00000001", 0.5, 25000),
            ],
        )
        self.compare(
            xml_to_dict(
                self.get_file_contents("aka/tests/resources/payroll_request.xml")
            ),
            xml_to_dict(request.xml),
            "",
        )

    def test_create_payroll_response_parse(self):
        response = PrismePayrollResponse(
            None, self.get_file_contents("aka/tests/resources/payroll_response.xml")
        )
        self.assertEqual("5637238342", response.rec_id)

    # POSITIVE TESTS

    def test_payroll_success(self):
        # Contains just the required fields
        file = File(open("aka/tests/resources/payroll.csv", "rb"))
        formData = {"year": 2019, "month": 11, "total_amount": "1000", "file": file}
        response = self.client.post(self.url, formData)
        file.close()
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        el = root.xpath("//ul[@class='success-list']/li")
        self.assertEqual(1, len(el))
        self.assertEqual("1234", el[0].text)

    # NEGATIVE TESTS

    def test_payroll_failure_missing_year(self):
        formData = {
            "month": 11,
            "total_amount": 200,
            "form-0-cpr": "1234567890",
            "form-0-agreement_number": "1",
            "form-0-amount": 200,
            "form-0-net_salary": 40000,
            "form-TOTAL_FORMS": 1,
            "form-INITIAL_FORMS": 0,
            "form-MIN_NUM_FORMS": 0,
            "form-MAX_NUM_FORMS": 1000,
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        erroritems = root.xpath(
            "//div[@data-field='id_year']//ul[@class='errorlist']/li"
        )
        self.assertEqual(1, len(erroritems))
        self.assertEqual("error.required", erroritems[0].attrib.get("data-trans"))

    def test_payroll_failure_missing_month(self):
        formData = {
            "year": 2019,
            "total_amount": 200,
            "form-0-agreement_number": "1",
            "form-0-amount": 200,
            "form-0-net_salary": 40000,
            "form-TOTAL_FORMS": 1,
            "form-INITIAL_FORMS": 0,
            "form-MIN_NUM_FORMS": 0,
            "form-MAX_NUM_FORMS": 1000,
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        erroritems = root.xpath(
            "//div[@data-field='id_month']//ul[@class='errorlist']/li"
        )
        self.assertEqual(1, len(erroritems))
        self.assertEqual("error.required", erroritems[0].attrib.get("data-trans"))

    def test_payroll_failure_missing_total_amount(self):
        formData = {
            "year": 2019,
            "month": 11,
            "form-0-cpr": "1234567890",
            "form-0-agreement_number": "1",
            "form-0-amount": 200,
            "form-0-net_salary": 40000,
            "form-TOTAL_FORMS": 1,
            "form-INITIAL_FORMS": 0,
            "form-MIN_NUM_FORMS": 0,
            "form-MAX_NUM_FORMS": 1000,
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        erroritems = root.xpath(
            "//div[@data-field='id_total_amount']//ul[@class='errorlist']/li"
        )
        self.assertEqual(1, len(erroritems))
        self.assertEqual("error.required", erroritems[0].attrib.get("data-trans"))

    def test_payroll_failure_sum_mismatch(self):
        file = File(open("aka/tests/resources/payroll.csv", "rb"))
        formData = {"year": 2019, "month": 11, "total_amount": "1200", "file": file}
        response = self.client.post(self.url, formData)
        file.close()
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        erroritems = root.xpath(
            "//div[@data-field='id_total_amount']//ul[@class='errorlist']/li"
        )
        self.assertEqual(1, len(erroritems))
        self.assertEqual(
            "loentraek.sum_mismatch", erroritems[0].attrib.get("data-trans")
        )

    def test_payroll_failure_incorrect_csv(self):
        file = File(open("aka/tests/resources/incorrect.csv", "rb"))
        formData = {"year": 2019, "month": 11, "total_amount": "1000", "file": file}
        response = self.client.post(self.url, formData)
        file.close()
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        erroritems = root.xpath(
            "//div[@data-field='id_file']//ul[@class='errorlist']/li"
        )
        self.assertEqual(1, len(erroritems))
        self.assertEqual(
            "error.upload_no_encoding", erroritems[0].attrib.get("data-trans")
        )

    def test_payroll_failure_empty_csv(self):
        file = File(open("aka/tests/resources/payroll_empty.csv", "rb"))
        formData = {"year": 2019, "month": 11, "total_amount": "1000", "file": file}
        response = self.client.post(self.url, formData)
        file.close()
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        erroritems = root.xpath(
            "//div[@data-field='id_file']//ul[@class='errorlist']/li"
        )
        self.assertEqual(1, len(erroritems))
        self.assertEqual("error.upload_empty", erroritems[0].attrib.get("data-trans"))
