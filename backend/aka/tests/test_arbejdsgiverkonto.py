from decimal import Decimal

import logging
from datetime import date

from aka.clients.prisme import PrismeAccountRequest, PrismeAccountResponse
from aka.tests.mixins import TestMixin
from django.test import TestCase
from xmltodict import parse as xml_to_dict

from aka.clients.prisme import PrismeSELAccountResponse


class BasicTestCase(TestMixin, TestCase):
    def setUp(self):
        super(BasicTestCase, self).setUp()
        logging.disable(logging.CRITICAL)
        self.url = "/konto/"
        self.dafomock = self.mock("aka.clients.dafo.Dafo.lookup_cvr")
        self.dafomock.return_value = {
            "navn": "Testfirma",
            "adresse": "Testvej 42",
            "postnummer": "1234",
            "bynavn": "Testby",
            "landekode": "DK",
        }

        session = self.client.session
        session["user_info"] = {"cvr": "12345678"}
        session.save()

        self.prisme_return = {
            "PrismeAccountRequest": PrismeAccountResponse(
                None,
                self.get_file_contents(
                    "aka/tests/resources/employeraccount_response.xml"
                ),
            )
        }

    # PRISME INTERFACE TESTS #

    def test_account_request_parse(self):
        request = PrismeAccountRequest(
            "12345678", date(2019, 1, 22), date(2019, 1, 22), 0
        )
        self.compare(
            xml_to_dict(
                self.get_file_contents(
                    "aka/tests/resources/employeraccount_request.xml"
                )
            ),
            xml_to_dict(request.xml),
            "",
        )

    def test_account_response_parse(self):
        response = PrismeSELAccountResponse(
            None,
            self.get_file_contents("aka/tests/resources/employeraccount_response.xml"),
        )
        self.assertEqual(1, len(response.transactions))
        transaction0 = response.transactions[0]
        self.assertEqual("00000001", transaction0.account_number)
        self.assertEqual("2018-01-03", transaction0.transaction_date)
        self.assertEqual("2019-01-22", transaction0.accounting_date)
        self.assertEqual("183000", transaction0.debitor_group_id)
        self.assertEqual(None, transaction0.debitor_group_name)
        self.assertEqual("AKI-30000000", transaction0.voucher)
        self.assertEqual(None, transaction0.text)
        self.assertEqual(None, transaction0.payment_code)
        self.assertEqual(None, transaction0.payment_code_name)
        self.assertEqual(Decimal(200.0), transaction0.amount)
        self.assertEqual(Decimal("37.05"), transaction0.remaining_amount)
        self.assertEqual("2018-01-03", transaction0.due_date)
        self.assertEqual(None, transaction0.closed_date)
        self.assertEqual("KMO-000000001", transaction0.last_settlement_voucher)
        self.assertEqual(None, transaction0.collection_letter_date)
        self.assertEqual("Ingen", transaction0.collection_letter_code)
        self.assertEqual(None, transaction0.claim_type_code)
        self.assertEqual("AKI-000001", transaction0.invoice_number)
        self.assertEqual("Debitor", transaction0.transaction_type)
        self.assertEqual("2", transaction0.rate_number)
