import json
import logging
from unittest.mock import patch

from aka.clients.prisme import PrismeInterestNoteRequest, PrismeInterestNoteResponse
from aka.tests.mixins import TestMixin
from django.test import TestCase
from django.test import override_settings
from xmltodict import parse as xml_to_dict


@override_settings(OPENID_CONNECT={'enabled': False})
class BasicTestCase(TestMixin, TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.url = '/rentenota'
        soap_patch = patch('aka.clients.prisme.Prisme.process_service')
        self.soapmock = soap_patch.start()
        self.addCleanup(soap_patch.stop)

        dafo_patch = patch('aka.clients.dafo.Dafo.lookup_cvr')
        self.dafomock = dafo_patch.start()
        self.addCleanup(dafo_patch.stop)


    ### PRISME INTERFACE TESTS ###

    def test_interest_note_request_parse(self):
        request = PrismeInterestNoteRequest('10977231', 2019, 4)
        self.compare(
            xml_to_dict(self.get_file_contents('aka/tests/resources/interestnote_request.xml')),
            xml_to_dict(request.xml),
            ""
        )

    def test_interest_note_response_parse(self):
        response = PrismeInterestNoteResponse(None, self.get_file_contents('aka/tests/resources/interestnote_response.xml'))
        self.assertEqual(2, len(response.interest_journal))
        journal0 = response.interest_journal[0]
        self.assertEqual("03-04-2019", journal0.updated)
        self.assertEqual("00000725", journal0.account_number)
        self.assertEqual("00000001", journal0.interest_note)
        self.assertEqual("02-04-2019", journal0.to_date)
        self.assertEqual("200", journal0.billing_classification)
        self.assertEqual(1, len(journal0.interest_transactions))
        transaction00 = journal0.interest_transactions[0]

        self.assertEqual("FAK-00000040", transaction00.voucher)
        self.assertEqual("Renter af fakturanummer 00000044", transaction00.text)
        self.assertEqual("02-01-2018", transaction00.due_date)
        self.assertEqual("4000.00", transaction00.invoice_amount)
        self.assertEqual("160.00", transaction00.interest_amount)
        self.assertEqual("02-01-2018", transaction00.transaction_date)
        self.assertEqual("00000044", transaction00.invoice)
        self.assertEqual("01-01-2019", transaction00.calculate_from_date)
        self.assertEqual(None, transaction00.calculate_to_date)
        self.assertEqual("0", transaction00.interest_days)

        journal1 = response.interest_journal[1]
        self.assertEqual("03-04-2019", journal1.updated)
        self.assertEqual("00000726", journal1.account_number)
        self.assertEqual("00000002", journal1.interest_note)
        self.assertEqual("02-04-2019", journal1.to_date)
        self.assertEqual("200", journal1.billing_classification)
        self.assertEqual(1, len(journal1.interest_transactions))

        transaction10 = journal1.interest_transactions[0]
        self.assertEqual("FAK-00000039", transaction10.voucher)
        self.assertEqual("Renter af fakturanummer 00000043", transaction10.text)
        self.assertEqual("02-01-2018", transaction10.due_date)
        self.assertEqual("7000.00", transaction10.invoice_amount)
        self.assertEqual("280.00", transaction10.interest_amount)
        self.assertEqual("02-01-2018", transaction10.transaction_date)
        self.assertEqual("00000043", transaction10.invoice)
        self.assertEqual("01-01-2019", transaction10.calculate_from_date)
        self.assertEqual(None, transaction10.calculate_to_date)
        self.assertEqual("0", transaction10.interest_days)


    ### POSITIVE TESTS ###

    def checkReturnValIsJSON(self, response):
        try:
            charset = response.charset
            json.dumps(json.loads(response.content.decode(charset)), indent=4)
        except json.decoder.JSONDecodeError:
            self.fail('Did not get JSON back.')


    ### NEGATIVE TESTS ###

    def test_invalid_cvr(self):
        expected = {'errors': ['Access denied'], 'fieldErrors': []}
        for y in range(2000, 2019):
            for m in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
                response = self.client.get(self.url + f'/{y}/{m}')
                self.assertEqual(response.status_code, 403)
                self.assertEqual(json.loads(response.content), expected)

    # def test_valid_cvr(self):
    #     request_factory = RequestFactory()
    #     session_handler = SessionMiddleware()
    #     self.soapmock.return_value = [PrismeInterestNoteResponse(self.get_file_contents('aka/tests/resources/interestnote_response.xml'))]
    #     self.dafomock.return_value = {'navn': 'Test company', 'adresse': 'Test Street 42', 'postnummer': 1234, 'bynavn': 'Test town', 'landekode': 'GL'}
    #     for y in range(2000, 2019):
    #         for m in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
    #             request = request_factory.get(self.url + f'/{y}/{m}')
    #             session_handler.process_request(request)
    #             request.session['user_info'] = {'CVR': '12345678'}
    #             response = RenteNotaView.as_view()(request, y, m)
    #             self.assertEqual(response.status_code, 200)
    #             self.checkReturnValIsJSON(response)

    @staticmethod
    def get_file_contents(filename):
        with open(filename, "r") as f:
            return f.read()
