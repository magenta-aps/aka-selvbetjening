from django.test import TestCase
from aka.helpers.prisme import Prisme, PrismeClaimant, PrismeInterestNote

class BasicTestCase(TestCase):
    def setUp(self):
        self.p = Prisme()

    # Test module Prisme.
    # -------------------
    def test_Prisme_1(self):
        self.assertTrue(type(self.p) is Prisme)
        try:
            self.p.sendToPrisme('some data')
        except Exception:
            self.fail('Failed call to sendToPrisme')

    def test_rentenota(self):
        rn = self.p.getRentenota(('2019', '01'))
        self.assertTrue(rn.status)

    def test_check_cvr_parse(self):
        item = PrismeClaimant("""
            <FujClaimant>
                <ClaimantId>35SKATDK</ClaimantId>
                <ClaimantId>35BIDRAGDK</ClaimantId>
            </FujClaimant>
        """)
        self.assertEqual(2, len(item.claimant_id))
        self.assertEqual("35SKATDK", item.claimant_id[0])
        self.assertEqual("35BIDRAGDK", item.claimant_id[1])

    def test_interest_note_parse(self):
        item = PrismeInterestNote("""
            <CustTable>
                <CustInterestJour>
                    <Updated>03-04-2019</Updated>
                    <AccountNum>00000725</AccountNum>
                    <InterestNote>00000001</InterestNote>
                    <ToDate>02-04-2019</ToDate>
                    <BillingClassification>200</BillingClassification>
                    <CustInterestTransactions>
                        <CustInterestTrans>
                            <Voucher>FAK-00000040</Voucher>
                            <Txt>Renter af fakturanummer 00000044 </Txt>
                            <DueDate>02-01-2018</DueDate>
                            <InvoiceAmount>4000.00</InvoiceAmount>
                            <InterestAmount>160.00</InterestAmount>
                            <TransDate>02-01-2018</TransDate>
                            <Invoice>00000044</Invoice>
                            <CalcFrom>01-01-2019</CalcFrom>
                            <CalcTo/>
                            <InterestDays>0</InterestDays>
                        </CustInterestTrans>
                    </CustInterestTransactions>
                </CustInterestJour>
                <CustInterestJour>
                    <Updated>03-04-2019</Updated>
                    <AccountNum>00000726</AccountNum>
                    <InterestNote>00000002</InterestNote>
                    <ToDate>02-04-2019</ToDate>
                    <BillingClassification>200</BillingClassification>
                    <CustInterestTransactions>
                        <CustInterestTrans>
                            <Voucher>FAK-00000039</Voucher>
                            <Txt>Renter af fakturanummer 00000043 </Txt>
                            <DueDate>02-01-2018</DueDate>
                            <InvoiceAmount>7000.00</InvoiceAmount>
                            <InterestAmount>280.00</InterestAmount>
                            <TransDate>02-01-2018</TransDate>
                            <Invoice>00000043</Invoice>
                            <CalcFrom>01-01-2019</CalcFrom>
                            <CalcTo/>
                            <InterestDays>0</InterestDays>
                        </CustInterestTrans>
                    </CustInterestTransactions>
                </CustInterestJour>
            </CustTable>
        """)
        self.assertEqual(2, len(item.cust_interest_journal))
        journal0 = item.cust_interest_journal[0]
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
        self.assertEqual("01-01-2019", transaction00.calculate_from)
        self.assertEqual(None, transaction00.calculate_to)
        self.assertEqual("0", transaction00.interest_days)

        journal1 = item.cust_interest_journal[1]
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
        self.assertEqual("01-01-2019", transaction10.calculate_from)
        self.assertEqual(None, transaction10.calculate_to)
        self.assertEqual("0", transaction10.interest_days)
