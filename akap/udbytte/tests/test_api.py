# SPDX-FileCopyrightText: 2023 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: MPL-2.0

from datetime import datetime
from unittest.mock import ANY

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware
from udbytte.models import U1A, U1AItem


class UdbytteAPITest(TestCase):
    maxDiff = None

    def setUp(self):
        self.api_secret = "supersecret"

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
            dato_vedtagelse="2023-01-01",
            underskriftsberettiget="Yes",
            oprettet_af_cpr="1234567890",
            oprettet_af_cvr="12345678",
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
            cpr_cvr_tin="1234567891",
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
            navn="Lorem Ipsiu",
            revisionsfirma="Firm B",
            virksomhedsnavn="Company B",
            cvr="12345679",
            email="lorem@example.com",
            regnskabsår=2024,
            u1_udfyldt="False",
            udbytte=337,
            noter="Another note",
            by="City B",
            dato="2024-05-05",
            dato_vedtagelse="2024-05-05",
            underskriftsberettiget="UnderskriftsPerson",
            oprettet_af_cpr="1234567892",
            oprettet_af_cvr="12345679",
        )

        cls.u1a_item_3 = U1AItem.objects.create(
            u1a=cls.u1a_2,
            cpr_cvr_tin="1234567892",
            navn="Item 3",
            adresse="Address 3",
            postnummer="1000",
            by="City C",
            land="Denmark",
            udbytte=1000,
        )

        U1AItem.objects.filter(id=cls.u1a_item_3.id).update(
            oprettet=make_aware(datetime(2024, 3, 1, 12, 0, 0))
        )

    def test_get_u1a_entries(self):
        print("test_get_u1a_entries")
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_list"),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
        )
        print("resp:")
        print(resp)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            {
                "count": 2,
                "items": [
                    {
                        "by": "City A",
                        "cvr": "12345678",
                        "dato": "2023-01-01",
                        "dato_vedtagelse": "2023-01-01",
                        "email": "john@example.com",
                        "id": 1,
                        "navn": "John Doe",
                        "noter": "Test note",
                        "oprettet": ANY,
                        "oprettet_af_cpr": "1234567890",
                        "oprettet_af_cvr": "12345678",
                        "regnskabsår": 2023,
                        "revisionsfirma": "Firm A",
                        "u1_udfyldt": True,
                        "udbytte": "1337.00",
                        "underskriftsberettiget": "Yes",
                        "virksomhedsnavn": "Company A",
                    },
                    {
                        "by": "City B",
                        "cvr": "12345679",
                        "dato": "2024-05-05",
                        "dato_vedtagelse": "2024-05-05",
                        "email": "lorem@example.com",
                        "id": 2,
                        "navn": "Lorem Ipsiu",
                        "noter": "Another note",
                        "oprettet": ANY,
                        "oprettet_af_cpr": "1234567892",
                        "oprettet_af_cvr": "12345679",
                        "regnskabsår": 2024,
                        "revisionsfirma": "Firm B",
                        "u1_udfyldt": False,
                        "udbytte": "337.00",
                        "underskriftsberettiget": "UnderskriftsPerson",
                        "virksomhedsnavn": "Company B",
                    },
                ],
            },
        )

    def test_get_u1a_entries_by_year(self):
        # YEAR 2000 - does not exist!
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_list"),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
            data={"year": 2000},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            {
                "count": 0,
                "items": [],
            },
        )

        # YEAR 2023 - exists
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_list"),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
            data={"year": 2023},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            {
                "count": 1,
                "items": [
                    {
                        "by": "City A",
                        "cvr": "12345678",
                        "dato": "2023-01-01",
                        "dato_vedtagelse": "2023-01-01",
                        "email": "john@example.com",
                        "id": 1,
                        "navn": "John Doe",
                        "noter": "Test note",
                        "oprettet": ANY,
                        "oprettet_af_cpr": "1234567890",
                        "oprettet_af_cvr": "12345678",
                        "regnskabsår": 2023,
                        "revisionsfirma": "Firm A",
                        "u1_udfyldt": True,
                        "udbytte": "1337.00",
                        "underskriftsberettiget": "Yes",
                        "virksomhedsnavn": "Company A",
                    },
                ],
            },
        )

    def test_get_u1a_entries_by_cpr(self):
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_list"),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
            data={"cpr": self.u1a_item_1.cpr_cvr_tin},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            {
                "count": 1,
                "items": [
                    {
                        "id": 1,
                        "by": "City A",
                        "cvr": "12345678",
                        "dato": "2023-01-01",
                        "dato_vedtagelse": "2023-01-01",
                        "email": "john@example.com",
                        "navn": "John Doe",
                        "noter": "Test note",
                        "oprettet": ANY,
                        "oprettet_af_cpr": "1234567890",
                        "oprettet_af_cvr": "12345678",
                        "regnskabsår": 2023,
                        "revisionsfirma": "Firm A",
                        "u1_udfyldt": True,
                        "udbytte": "1337.00",
                        "underskriftsberettiget": "Yes",
                        "virksomhedsnavn": "Company A",
                    }
                ],
            },
        )

    def test_get_u1a_item_entries(self):
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_item_list"),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            {
                "count": 3,
                "items": [
                    {
                        "adresse": "Address 1",
                        "by": "City A",
                        "cpr_cvr_tin": "1234567890",
                        "id": 1,
                        "land": "Denmark",
                        "navn": "Item 1",
                        "oprettet": ANY,
                        "postnummer": "1000",
                        "u1a": {
                            "by": "City A",
                            "cvr": "12345678",
                            "dato": "2023-01-01",
                            "dato_vedtagelse": "2023-01-01",
                            "email": "john@example.com",
                            "id": 1,
                            "navn": "John Doe",
                            "noter": "Test note",
                            "oprettet": ANY,
                            "oprettet_af_cpr": "1234567890",
                            "oprettet_af_cvr": "12345678",
                            "regnskabsår": 2023,
                            "revisionsfirma": "Firm A",
                            "u1_udfyldt": True,
                            "udbytte": "1337.00",
                            "underskriftsberettiget": "Yes",
                            "virksomhedsnavn": "Company A",
                        },
                        "udbytte": "1000.00",
                    },
                    {
                        "adresse": "Address 2",
                        "by": "City B",
                        "cpr_cvr_tin": "1234567891",
                        "id": 2,
                        "land": "Sweden",
                        "navn": "Item 2",
                        "oprettet": ANY,
                        "postnummer": "2000",
                        "u1a": {
                            "by": "City A",
                            "cvr": "12345678",
                            "dato": "2023-01-01",
                            "dato_vedtagelse": "2023-01-01",
                            "email": "john@example.com",
                            "id": 1,
                            "navn": "John Doe",
                            "noter": "Test note",
                            "oprettet": ANY,
                            "oprettet_af_cpr": "1234567890",
                            "oprettet_af_cvr": "12345678",
                            "regnskabsår": 2023,
                            "revisionsfirma": "Firm A",
                            "u1_udfyldt": True,
                            "udbytte": "1337.00",
                            "underskriftsberettiget": "Yes",
                            "virksomhedsnavn": "Company A",
                        },
                        "udbytte": "337.00",
                    },
                    {
                        "adresse": "Address 3",
                        "by": "City C",
                        "cpr_cvr_tin": "1234567892",
                        "id": 3,
                        "land": "Denmark",
                        "navn": "Item 3",
                        "oprettet": ANY,
                        "postnummer": "1000",
                        "u1a": {
                            "by": "City B",
                            "cvr": "12345679",
                            "dato": "2024-05-05",
                            "dato_vedtagelse": "2024-05-05",
                            "email": "lorem@example.com",
                            "id": 2,
                            "navn": "Lorem Ipsiu",
                            "noter": "Another note",
                            "oprettet": ANY,
                            "oprettet_af_cpr": "1234567892",
                            "oprettet_af_cvr": "12345679",
                            "regnskabsår": 2024,
                            "revisionsfirma": "Firm B",
                            "u1_udfyldt": False,
                            "udbytte": "337.00",
                            "underskriftsberettiget": "UnderskriftsPerson",
                            "virksomhedsnavn": "Company B",
                        },
                        "udbytte": "1000.00",
                    },
                ],
            },
        )

    def test_get_u1a_item_entries_by_year(self):
        # YEAR 2000 - does not exist
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_item_list"),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
            data={"year": 2000},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            {
                "count": 0,
                "items": [],
            },
        )

        # YEAR 2023 - exists
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_item_list"),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
            data={"year": 2023},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            {
                "count": 2,
                "items": [
                    {
                        "adresse": "Address 1",
                        "by": "City A",
                        "cpr_cvr_tin": "1234567890",
                        "id": 1,
                        "land": "Denmark",
                        "navn": "Item 1",
                        "oprettet": ANY,
                        "postnummer": "1000",
                        "u1a": {
                            "by": "City A",
                            "cvr": "12345678",
                            "dato": "2023-01-01",
                            "dato_vedtagelse": "2023-01-01",
                            "email": "john@example.com",
                            "id": 1,
                            "navn": "John Doe",
                            "noter": "Test note",
                            "oprettet": ANY,
                            "oprettet_af_cpr": "1234567890",
                            "oprettet_af_cvr": "12345678",
                            "regnskabsår": 2023,
                            "revisionsfirma": "Firm A",
                            "u1_udfyldt": True,
                            "udbytte": "1337.00",
                            "underskriftsberettiget": "Yes",
                            "virksomhedsnavn": "Company A",
                        },
                        "udbytte": "1000.00",
                    },
                    {
                        "adresse": "Address 2",
                        "by": "City B",
                        "cpr_cvr_tin": "1234567891",
                        "id": 2,
                        "land": "Sweden",
                        "navn": "Item 2",
                        "oprettet": ANY,
                        "postnummer": "2000",
                        "u1a": {
                            "by": "City A",
                            "cvr": "12345678",
                            "dato": "2023-01-01",
                            "dato_vedtagelse": "2023-01-01",
                            "email": "john@example.com",
                            "id": 1,
                            "navn": "John Doe",
                            "noter": "Test note",
                            "oprettet": ANY,
                            "oprettet_af_cpr": "1234567890",
                            "oprettet_af_cvr": "12345678",
                            "regnskabsår": 2023,
                            "revisionsfirma": "Firm A",
                            "u1_udfyldt": True,
                            "udbytte": "1337.00",
                            "underskriftsberettiget": "Yes",
                            "virksomhedsnavn": "Company A",
                        },
                        "udbytte": "337.00",
                    },
                ],
            },
        )

    def test_get_u1a_item_entries_by_filter(self):
        # Filter by U1A-id
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_item_list"),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
            data={"u1a": self.u1a_1.id},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            {
                "count": 2,
                "items": [
                    {
                        "adresse": "Address 1",
                        "by": "City A",
                        "cpr_cvr_tin": "1234567890",
                        "id": 1,
                        "land": "Denmark",
                        "navn": "Item 1",
                        "oprettet": ANY,
                        "postnummer": "1000",
                        "u1a": {
                            "by": "City A",
                            "cvr": "12345678",
                            "dato": "2023-01-01",
                            "dato_vedtagelse": "2023-01-01",
                            "email": "john@example.com",
                            "id": 1,
                            "navn": "John Doe",
                            "noter": "Test note",
                            "oprettet": ANY,
                            "oprettet_af_cpr": "1234567890",
                            "oprettet_af_cvr": "12345678",
                            "regnskabsår": 2023,
                            "revisionsfirma": "Firm A",
                            "u1_udfyldt": True,
                            "udbytte": "1337.00",
                            "underskriftsberettiget": "Yes",
                            "virksomhedsnavn": "Company A",
                        },
                        "udbytte": "1000.00",
                    },
                    {
                        "adresse": "Address 2",
                        "by": "City B",
                        "cpr_cvr_tin": "1234567891",
                        "id": 2,
                        "land": "Sweden",
                        "navn": "Item 2",
                        "oprettet": ANY,
                        "postnummer": "2000",
                        "u1a": {
                            "by": "City A",
                            "cvr": "12345678",
                            "dato": "2023-01-01",
                            "dato_vedtagelse": "2023-01-01",
                            "email": "john@example.com",
                            "id": 1,
                            "navn": "John Doe",
                            "noter": "Test note",
                            "oprettet": ANY,
                            "oprettet_af_cpr": "1234567890",
                            "oprettet_af_cvr": "12345678",
                            "regnskabsår": 2023,
                            "revisionsfirma": "Firm A",
                            "u1_udfyldt": True,
                            "udbytte": "1337.00",
                            "underskriftsberettiget": "Yes",
                            "virksomhedsnavn": "Company A",
                        },
                        "udbytte": "337.00",
                    },
                ],
            },
        )

        # Test filtering (by / city)
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_item_list"),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
            data={"by": "City B"},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            {
                "count": 1,
                "items": [
                    {
                        "adresse": "Address 2",
                        "by": "City B",
                        "cpr_cvr_tin": "1234567891",
                        "id": 2,
                        "land": "Sweden",
                        "navn": "Item 2",
                        "oprettet": ANY,
                        "postnummer": "2000",
                        "u1a": {
                            "by": "City A",
                            "cvr": "12345678",
                            "dato": "2023-01-01",
                            "dato_vedtagelse": "2023-01-01",
                            "email": "john@example.com",
                            "id": 1,
                            "navn": "John Doe",
                            "noter": "Test note",
                            "oprettet": ANY,
                            "oprettet_af_cpr": "1234567890",
                            "oprettet_af_cvr": "12345678",
                            "regnskabsår": 2023,
                            "revisionsfirma": "Firm A",
                            "u1_udfyldt": True,
                            "udbytte": "1337.00",
                            "underskriftsberettiget": "Yes",
                            "virksomhedsnavn": "Company A",
                        },
                        "udbytte": "337.00",
                    },
                ],
            },
        )

        # Test date filtering (oprettet_efter)
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_item_list"),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
            data={"oprettet_efter": "2024-02-01"},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            {
                "count": 2,
                "items": [
                    {
                        "adresse": "Address 2",
                        "by": "City B",
                        "cpr_cvr_tin": "1234567891",
                        "id": 2,
                        "land": "Sweden",
                        "navn": "Item 2",
                        "oprettet": ANY,
                        "postnummer": "2000",
                        "u1a": {
                            "by": "City A",
                            "cvr": "12345678",
                            "dato": "2023-01-01",
                            "dato_vedtagelse": "2023-01-01",
                            "email": "john@example.com",
                            "id": 1,
                            "navn": "John Doe",
                            "noter": "Test note",
                            "oprettet": ANY,
                            "oprettet_af_cpr": "1234567890",
                            "oprettet_af_cvr": "12345678",
                            "regnskabsår": 2023,
                            "revisionsfirma": "Firm A",
                            "u1_udfyldt": True,
                            "udbytte": "1337.00",
                            "underskriftsberettiget": "Yes",
                            "virksomhedsnavn": "Company A",
                        },
                        "udbytte": "337.00",
                    },
                    {
                        "adresse": "Address 3",
                        "by": "City C",
                        "cpr_cvr_tin": "1234567892",
                        "id": 3,
                        "land": "Denmark",
                        "navn": "Item 3",
                        "oprettet": ANY,
                        "postnummer": "1000",
                        "u1a": {
                            "by": "City B",
                            "cvr": "12345679",
                            "dato": "2024-05-05",
                            "dato_vedtagelse": "2024-05-05",
                            "email": "lorem@example.com",
                            "id": 2,
                            "navn": "Lorem Ipsiu",
                            "noter": "Another note",
                            "oprettet": ANY,
                            "oprettet_af_cpr": "1234567892",
                            "oprettet_af_cvr": "12345679",
                            "regnskabsår": 2024,
                            "revisionsfirma": "Firm B",
                            "u1_udfyldt": False,
                            "udbytte": "337.00",
                            "underskriftsberettiget": "UnderskriftsPerson",
                            "virksomhedsnavn": "Company B",
                        },
                        "udbytte": "1000.00",
                    },
                ],
            },
        )

    def test_get_u1a_items_unique_cprs(self):
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_item_unique_cprs"),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            {"count": 3, "items": ["1234567890", "1234567891", "1234567892"]},
        )

    def test_get_u1a_items_unique_cprs_by_year(self):
        # YEAR 2000 - does not exist
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_item_unique_cprs"),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
            data={"year": 2000},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(),
            {"count": 0, "items": []},
        )

        # YEAR 2023 - contains 2 CPRs
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_item_unique_cprs"),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
            data={"year": 2023},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json(), {"count": 2, "items": ["1234567890", "1234567891"]}
        )

        # YEAR 2024 - contains 1 CPR
        resp = self.client.get(
            reverse("udbytte:api-1.0.0:u1a_item_unique_cprs"),
            HTTP_AUTHORIZATION=f"Bearer {self.api_secret}",
            data={"year": 2024},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"count": 1, "items": ["1234567892"]})
