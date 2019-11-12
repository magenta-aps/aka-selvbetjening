from datetime import date

from aka.clients.prisme import PrismeClaimRequest, PrismeClaimResponse, Prisme
from aka.clients.prisme import PrismeCvrCheckRequest, PrismeCvrCheckResponse
from aka.clients.prisme import PrismeImpairmentRequest, PrismeImpairmentResponse
from aka.clients.prisme import PrismeInterestNoteRequest, PrismeInterestNoteResponse
from django.core.files import File
from django.test import SimpleTestCase
from xmltodict import parse as xml_to_dict


class BasicTestCase(SimpleTestCase):

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

    def test_create_claim_request_parse(self):
        attachment = File(open('aka/tests/resources/testfile.pdf'))
        attachment.close()
        request = PrismeClaimRequest(
            claimant_id="32SE",
            cpr_cvr="0102030405",
            external_claimant="Ekstern fordringshaver",
            claim_group_number=4,
            claim_type=1,
            child_cpr=None,
            claim_ref=1234,
            amount_balance=20,
            text="Udlæg for hotdog",
            created_by="TesterPerson",
            period_start=date(2019, 3, 7),
            period_end=date(2019, 3, 8),
            due_date=date(2019, 4, 1),
            founded_date=date(2019, 3, 7),
            obsolete_date=date(2019, 5, 1),
            notes="Den smagte godt",
            codebtors=[11223344, 55667788],
            files=[attachment]
        )
        self.compare(
            xml_to_dict(self.get_file_contents('aka/tests/resources/claim_request.xml')),
            xml_to_dict(request.xml),
            ""
        )

    def test_create_claim_response_parse(self):
        response = PrismeClaimResponse(None, self.get_file_contents('aka/tests/resources/claim_response.xml'))
        self.assertEqual("5637238342", response.rec_id)

    def test_check_cvr_request_parse(self):
        request = PrismeCvrCheckRequest('12345678')
        self.compare(
            xml_to_dict(self.get_file_contents('aka/tests/resources/cvrcheck_request.xml')),
            xml_to_dict(request.xml),
            ""
        )

    def test_check_cvr_response_parse(self):
        response = PrismeCvrCheckResponse(None, self.get_file_contents('aka/tests/resources/cvrcheck_response.xml'))
        self.assertEqual(2, len(response.claimant_id))
        self.assertEqual("35SKATDK", response.claimant_id[0])
        self.assertEqual("35BIDRAGDK", response.claimant_id[1])

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

    @staticmethod
    def get_file_contents(filename):
        with open(filename, "r") as f:
            return f.read()

    def compare(self, a, b, path):
        self.assertEqual(type(a), type(b), f"mismatch on {path}, different type {type(a)} != {type(b)}")
        if isinstance(a, list):
            self.assertEqual(len(a), len(b), f"mismatch on {path}, different length {len(a)} != {len(b)}")
            for index, item in enumerate(a):
                self.compare(item, b[index], f"{path}[{index}]")
        elif isinstance(a, dict):
            self.compare(a.keys(), b.keys(), f"{path}.keys()")
            for key in a:
                self.compare(a[key], b[key], f"{path}[{key}]")
        else:
            self.assertEqual(a, b, f"mismatch on {path}, different value {a} != {b}")
