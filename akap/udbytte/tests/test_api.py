from datetime import datetime
from unittest.mock import ANY

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware
from udbytte.models import U1A, U1AItem


class UdbytteAPITest(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.u1a_1 = U1A.objects.create(
            navn="John Doe",
            revisionsfirma="Firm A",
            virksomhedsnavn="Company A",
            cvr="12345678",
            email="john@example.com",
            regnskabsår=2023,
            u1_udfyldt="True",
            udbytte=1337,
            noter="Test note",
            by="City A",
            dato="2023-01-01",
            underskriftsberettiget="Yes",
            oprettet_af_cpr="1234567890",
            oprettet_af_cvr="98765432",
        )

        cls.u1a_item_1 = U1AItem.objects.create(
            u1a=cls.u1a_1,
            cpr_cvr_tin="1234567890",
            navn="Item 1",
            adresse="Address 1",
            postnummer="1000",
            by="City A",
            land="Denmark",
            udbytte=1000,
        )
        cls.u1a_item_2 = U1AItem.objects.create(
            u1a=cls.u1a_1,
            cpr_cvr_tin="0987654321",
            navn="Item 2",
            adresse="Address 2",
            postnummer="2000",
            by="City B",
            land="Sweden",
            udbytte=337,
        )

        U1AItem.objects.filter(id=cls.u1a_item_1.id).update(
            oprettet=make_aware(datetime(2024, 1, 1, 12, 0, 0))
        )
        U1AItem.objects.filter(id=cls.u1a_item_2.id).update(
            oprettet=make_aware(datetime(2024, 2, 1, 12, 0, 0))
        )

        # Second test U1A
        cls.u1a_2 = U1A.objects.create(
            navn="Jane Smith",
            revisionsfirma="Firm B",
            virksomhedsnavn="Company B",
            cvr="87654321",
            email="jane@example.com",
            regnskabsår=2022,
            u1_udfyldt="False",
            udbytte=337,
            noter="Another note",
            by="City B",
            dato="2022-05-05",
            underskriftsberettiget="No",
            oprettet_af_cpr="0987654321",
            oprettet_af_cvr="12345678",
        )

    def setUp(self):
        self.api_secret = "supersecret"

    def test_get_u1a_entries(self):
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_list"),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
            data={"navn": self.u1a_1.navn},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            {
                "count": 1,
                "items": [
                    {
                        "id": self.u1a_1.id,
                        "navn": "John Doe",
                        "revisionsfirma": "Firm A",
                        "virksomhedsnavn": "Company A",
                        "cvr": "12345678",
                        "email": "john@example.com",
                        "regnskabsår": 2023,
                        "u1_udfyldt": True,
                        "udbytte": "1337.00",
                        "noter": "Test note",
                        "by": "City A",
                        "dato": "2023-01-01",
                        "underskriftsberettiget": "Yes",
                        "oprettet": ANY,
                        "oprettet_af_cpr": "1234567890",
                        "oprettet_af_cvr": "98765432",
                    },
                ],
            },
        )

    def test_get_u1a_item_entries(self):
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_item_list", args=[self.u1a_1.id]),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            {
                "count": 2,
                "items": [
                    {
                        "id": self.u1a_item_1.id,
                        "u1a": self.u1a_1.id,
                        "cpr_cvr_tin": "1234567890",
                        "navn": "Item 1",
                        "adresse": "Address 1",
                        "postnummer": "1000",
                        "by": "City A",
                        "land": "Denmark",
                        "udbytte": "1000.00",
                        "oprettet": ANY,
                    },
                    {
                        "id": self.u1a_item_2.id,
                        "u1a": self.u1a_1.id,
                        "cpr_cvr_tin": "0987654321",
                        "navn": "Item 2",
                        "adresse": "Address 2",
                        "postnummer": "2000",
                        "by": "City B",
                        "land": "Sweden",
                        "udbytte": "337.00",
                        "oprettet": ANY,
                    },
                ],
            },
        )

        # Test filtering
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_item_list", args=[self.u1a_1.id]),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
            data={"by": "City A"},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            {
                "count": 1,
                "items": [
                    {
                        "id": self.u1a_item_1.id,
                        "u1a": self.u1a_1.id,
                        "cpr_cvr_tin": "1234567890",
                        "navn": "Item 1",
                        "adresse": "Address 1",
                        "postnummer": "1000",
                        "by": "City A",
                        "land": "Denmark",
                        "udbytte": "1000.00",
                        "oprettet": ANY,
                    },
                ],
            },
        )

        # Test date filtering (oprettet_efter)
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_item_list", args=[self.u1a_1.id]),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
            data={"oprettet_efter": "2024-02-01"},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            {
                "count": 1,
                "items": [
                    {
                        "id": self.u1a_item_2.id,
                        "u1a": self.u1a_1.id,
                        "cpr_cvr_tin": "0987654321",
                        "navn": "Item 2",
                        "adresse": "Address 2",
                        "postnummer": "2000",
                        "by": "City B",
                        "land": "Sweden",
                        "udbytte": "337.00",
                        "oprettet": ANY,
                    },
                ],
            },
        )
