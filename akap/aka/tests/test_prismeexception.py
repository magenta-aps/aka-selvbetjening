from aka.clients.prisme import PrismeException
from django.test import SimpleTestCase


class BasicTestCase(SimpleTestCase):
    def testFordring(self):
        error = PrismeException(
            250,
            "Der findes ikke en inkassosag med det eksterne ref.nr. 1234",
            "fordring",
        )
        self.assertEqual(error.code, 250)
        self.assertEqual(
            error.text, "Der findes ikke en inkassosag med det eksterne ref.nr. 1234"
        )
        self.assertEqual(
            error.message, "Der findes ikke en inkassosag med det eksterne ref.nr. 1234"
        )
        self.assertDictEqual(
            error.params,
            {
                "refnumber": "1234",
                "text": "Der findes ikke en inkassosag med det eksterne ref.nr. 1234",
            },
        )

    def testNedskrivning(self):
        error = PrismeException(
            250,
            "Der findes ikke en inkassosag med det eksterne ref.nr. 1234",
            "fordring",
        )
        self.assertEqual(error.code, 250)
        self.assertEqual(
            error.text, "Der findes ikke en inkassosag med det eksterne ref.nr. 1234"
        )
        self.assertEqual(
            error.message, "Der findes ikke en inkassosag med det eksterne ref.nr. 1234"
        )
        self.assertDictEqual(
            error.params,
            {
                "refnumber": "1234",
                "text": "Der findes ikke en inkassosag med det eksterne ref.nr. 1234",
            },
        )

        error = PrismeException(
            250,
            "Det fremsendte beløb 2.000,00 er større end restsaldoen på inkassosagen 100,00",
            "nedskrivning",
        )
        self.assertEqual(error.code, 250)
        self.assertEqual(
            error.text,
            "Det fremsendte beløb 2.000,00 er større end restsaldoen på inkassosagen 100,00",
        )
        self.assertEqual(
            error.message,
            "Det fremsendte beløb 2.000,00 er større end restsaldoen på inkassosagen 100,00",
        )
        self.assertDictEqual(
            error.params,
            {
                "amount": "2.000,00",
                "saldo": "100,00",
                "text": "Det fremsendte beløb 2.000,00 er større end restsaldoen på inkassosagen 100,00",
            },
        )

    def testRentenota(self):
        error = PrismeException(
            250,
            "Der findes ingen renter for dette CPR/CVR 1234567890 eller for den angivne periode 05-12-2014 06-08-2018",
            "rentenota",
        )
        self.assertEqual(error.code, 250)
        self.assertEqual(
            error.text,
            "Der findes ingen renter for dette CPR/CVR 1234567890 eller for den angivne periode 05-12-2014 06-08-2018",
        )
        self.assertEqual(
            error.message,
            "Der findes ingen renter for dette CPR/CVR 1234567890 eller for den angivne periode 05-12-2014 06-08-2018",
        )
        self.assertDictEqual(
            error.params,
            {
                "cvr": "1234567890",
                "start": "05-12-2014",
                "end": "06-08-2018",
                "text": "Der findes ingen renter for dette CPR/CVR 1234567890 eller for den angivne periode 05-12-2014 06-08-2018",
            },
        )

    def testLoentraek(self):
        error = PrismeException(250, "Aftalenummer 1234-AB findes ikke", "loentraek")
        self.assertEqual(error.code, 250)
        self.assertEqual(error.text, "Aftalenummer 1234-AB findes ikke")
        self.assertEqual(error.message, "Aftalenummer 1234-AB findes ikke")
        self.assertDictEqual(
            error.params, {"nr": "1234-AB", "text": "Aftalenummer 1234-AB findes ikke"}
        )

        error = PrismeException(
            250,
            "Det samme CPR-Nummer 1234567890 må kun optræde en gang pr. indberetning",
            "loentraek",
        )
        self.assertEqual(error.code, 250)
        self.assertEqual(
            error.text,
            "Det samme CPR-Nummer 1234567890 må kun optræde en gang pr. indberetning",
        )
        self.assertEqual(
            error.message,
            "Det samme CPR-Nummer 1234567890 må kun optræde en gang pr. indberetning",
        )
        self.assertDictEqual(
            error.params,
            {
                "cpr": "1234567890",
                "text": "Det samme CPR-Nummer 1234567890 må kun optræde en gang pr. indberetning",
            },
        )

    def testAccount(self):
        error = PrismeException(
            250, "Der findes ingen debitorer for dette CPR/CVR", "loentraek"
        )
        self.assertEqual(error.code, 250)
        self.assertEqual(error.text, "Der findes ingen debitorer for dette CPR/CVR")
        self.assertEqual(error.message, "Der findes ingen debitorer for dette CPR/CVR")
        self.assertDictEqual(
            error.params, {"text": "Der findes ingen debitorer for dette CPR/CVR"}
        )
