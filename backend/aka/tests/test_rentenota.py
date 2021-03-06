import logging

from aka.clients.prisme import PrismeInterestNoteRequest, \
    PrismeInterestNoteResponse
from aka.tests.mixins import TestMixin
from django.test import TestCase
from django.test import override_settings
from lxml import etree
from xmltodict import parse as xml_to_dict


@override_settings(OPENID_CONNECT={'enabled': False})
class BasicTestCase(TestMixin, TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.url = '/rentenota/'
        self.soapmock = self.mock('aka.clients.prisme.Prisme.process_service')
        self.soapmock.return_value = [PrismeInterestNoteResponse(
            None,
            self.get_file_contents('aka/tests/resources/interestnote_response.xml')
        )]

        dafologinmock = self.mock('aka.clients.dafo.Dafo.login')
        dafologinmock.return_value = ""

        self.dafomock = self.mock('aka.clients.dafo.Dafo.lookup_cvr')
        self.dafomock.return_value = {
            'navn': 'Testfirma',
            'adresse': 'Testvej 42',
            'postnummer': '1234',
            'bynavn': 'Testby',
            'landekode': 'DK'
        }

        session = self.client.session
        session['user_info'] = {'CVR': '12479182'}
        session.save()

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

    def test_interestnote_success(self):
        response = self.client.get(self.url, {
            'year': 2019,
            'month': 10
        })
        self.assertEqual(response.status_code, 200)
        root = etree.fromstring(response.content, etree.HTMLParser())
        header_row = root.xpath("//table[@class='output-table']/thead/tr")[0]
        headers = [cell.text for cell in header_row.iterchildren()]
        rows = root.xpath("//table[@class='output-table']/tbody/tr[@class='rentenota-post-table-datarow']")
        data = [{headers[i]: cell.text for i, cell in enumerate(row.iterchildren())} for row in rows]
        self.assertEqual(2, len(data))
        self.assertEqual([
            {
                'Dato': '03-04-2019',
                'Debitor\xadkonto': '00000725',
                'Fakturerings\xadklassifikation': '200',
                'Bilag': 'FAK-00000040',
                'Rentenota\xadnummer': '00000001',
                'Tekst': 'Renter af fakturanummer 00000044',
                'Forfalds\xaddato': '02-01-2018',
                'Grundlag': '4000.00',
                'Beløb': '160.00',
                'Postdato': '02-01-2018',
                'Faktura': '00000044',
                'Fradato': '01-01-2019',
                'Tildato': 'None',
                'Dage': '0',
            },
            {
                'Dato': '03-04-2019',
                'Debitor\xadkonto': '00000726',
                'Fakturerings\xadklassifikation': '200',
                'Bilag': 'FAK-00000039',
                'Rentenota\xadnummer': '00000002',
                'Tekst': 'Renter af fakturanummer 00000043',
                'Forfalds\xaddato': '02-01-2018',
                'Grundlag': '7000.00',
                'Beløb': '280.00',
                'Postdato': '02-01-2018',
                'Faktura': '00000043',
                'Fradato': '01-01-2019',
                'Tildato': 'None',
                'Dage': '0',
            },
        ], data)
        rows = root.xpath("//table[@class='output-table']/tbody/tr[@class='rentenota-post-table-sumrow']")
        data = [cell.text for cell in rows[0].iterchildren()]
        self.assertEqual(3, len(data))
        self.assertEqual([None, '440,0', 'kr'], data)


    ### NEGATIVE TESTS ###

    def test_invalid_cvr(self):

        session = self.client.session
        session['user_info'] = None
        session.save()
        expected = {'errors': ['Access denied'], 'fieldErrors': []}
        for y in range(2000, 2019):
            for m in range(1, 13):
                response = self.client.get(self.url, {
                    'year': y,
                    'month': m
                })
                self.assertEqual(response.status_code, 403)
