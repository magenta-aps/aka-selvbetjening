# SPDX-FileCopyrightText: 2023 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: MPL-2.0

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

from aka.tests.mixins import TestMixin
from django.core.files import File
from django.template.response import TemplateResponse
from django.test import RequestFactory, TestCase, override_settings
from udbytte.models import U1A, U1AItem
from udbytte.views import UdbytteCreateView


class UdbytteViewTest(TestMixin, TestCase):
    def setUp(self):
        super(UdbytteViewTest, self).setUp()
        self.factory = RequestFactory()
        self.view = UdbytteCreateView.as_view()
        session = self.client.session
        session["user_info"] = {"cpr": "1234567890", "cvr": "12345678"}
        session["has_checked_cvr"] = True
        session.save()

    @override_settings(EMAIL_OFFICE_RECIPIENT="office@example.com")
    @patch(
        "udbytte.views.UdbytteCreateView.render_filled_form", return_value=b"PDF_DATA"
    )
    @patch("udbytte.views.UdbytteCreateView.send_mail_to_submitter")
    @patch("udbytte.views.UdbytteCreateView.get_csv", return_value=b"CSV_DATA")
    @patch("udbytte.views.UdbytteCreateView.save_files")
    @patch("udbytte.views.UdbytteCreateView.send_mail_to_office")
    def test_form_valid(
        self,
        mock_send_mail_to_office: MagicMock,
        mock_save_files: MagicMock,
        mock_get_csv: MagicMock,
        mock_send_mail_to_submitter: MagicMock,
        mock_render_filled_form: MagicMock,
    ):
        # Create form data
        form_data = {
            "navn": "Test User",
            "email": "test@example.com",
            "revisionsfirma": "Test Firm",
            "virksomhedsnavn": "Test Company",
            "cvr": "12345678",
            "regnskabsår": "2023",
            "u1_udfyldt": "0",
            "udbytte": Decimal("1337.00"),  # Use Decimal to match actual call
            "noter": "Test notes",
            "by": "Test City",
            "dato": date(2023, 1, 1),  # Use datetime.date to match actual call
            "dato_vedtagelse": date(
                2023, 1, 1
            ),  # Use datetime.date to match actual call
            "underskriftsberettiget": "Authorized User",
            "use_file": "",
        }

        formset_data = {
            "u1aitem_set-TOTAL_FORMS": "2",
            "u1aitem_set-INITIAL_FORMS": "0",
            "u1aitem_set-MIN_NUM_FORMS": "1",
            "u1aitem_set-MAX_NUM_FORMS": "1000",
            "u1aitem_set-0-cpr_cvr_tin": "1234567890",
            "u1aitem_set-0-navn": "Item 1",
            "u1aitem_set-0-adresse": "Address 1",
            "u1aitem_set-0-postnummer": "1000",
            "u1aitem_set-0-by": "City A",
            "u1aitem_set-0-land": "Denmark",
            "u1aitem_set-0-udbytte": "500.00",
            "u1aitem_set-1-cpr_cvr_tin": "0987654321",
            "u1aitem_set-1-navn": "Item 2",
            "u1aitem_set-1-adresse": "Address 2",
            "u1aitem_set-1-postnummer": "2000",
            "u1aitem_set-1-by": "City B",
            "u1aitem_set-1-land": "Sweden",
            "u1aitem_set-1-udbytte": "837.00",
        }

        # Make the POST request for the view
        request = self.factory.post("/udbytte/", {**form_data, **formset_data})
        session = self.client.session
        request.session = session
        request.user = MagicMock()

        # Call the view & assert
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, TemplateResponse)
        self.assertEqual(response.template_name, "udbytte/success.html")

        # Check database objects
        self.assertEqual(U1A.objects.count(), 1)
        u1a = U1A.objects.first()
        self.assertEqual(u1a.navn, "Test User")
        self.assertEqual(u1a.oprettet_af_cpr, "1234567890")

        self.assertEqual(U1AItem.objects.count(), 2)
        items = U1AItem.objects.all()
        self.assertEqual(items[0].navn, "Item 1")
        self.assertEqual(items[1].navn, "Item 2")

        # Verify mocked methods
        mock_render_filled_form.assert_called_once()
        mock_send_mail_to_submitter.assert_called_once_with(b"PDF_DATA")
        mock_get_csv.assert_called_once()
        mock_save_files.assert_called_once()
        mock_send_mail_to_office.assert_called_once_with(b"CSV_DATA", b"PDF_DATA")

    @override_settings(EMAIL_OFFICE_RECIPIENT="office@example.com")
    @patch(
        "udbytte.views.UdbytteCreateView.render_filled_form", return_value=b"PDF_DATA"
    )
    @patch("udbytte.views.UdbytteCreateView.send_mail_to_submitter")
    @patch("udbytte.views.UdbytteCreateView.get_csv", return_value=b"CSV_DATA")
    @patch("udbytte.views.UdbytteCreateView.save_files")
    @patch("udbytte.views.UdbytteCreateView.send_mail_to_office")
    def test_upload(
        self,
        mock_send_mail_to_office: MagicMock,
        mock_save_files: MagicMock,
        mock_get_csv: MagicMock,
        mock_send_mail_to_submitter: MagicMock,
        mock_render_filled_form: MagicMock,
    ):
        # Create form data
        form_data = {
            "navn": "Test User",
            "email": "test@example.com",
            "revisionsfirma": "Test Firm",
            "virksomhedsnavn": "Test Company",
            "cvr": "12345678",
            "regnskabsår": "2023",
            "u1_udfyldt": "0",
            "udbytte": Decimal("2700.00"),  # Use Decimal to match actual call
            "noter": "Test notes",
            "by": "Test City",
            "dato": date(2023, 1, 1),  # Use datetime.date to match actual call
            "dato_vedtagelse": date(
                2023, 1, 1
            ),  # Use datetime.date to match actual call
            "underskriftsberettiget": "Authorized User",
            "use_file": "1",
            "file": File(open("udbytte/tests/resources/test.xlsx", "rb")),
        }

        # Set up mock session data
        session = self.client.session
        session["user_info"] = {"cpr": "1234567890"}
        session.save()

        # Make the POST request for the view
        request = self.factory.post("/udbytte/", {**form_data})
        request.session = session
        request.user = MagicMock()
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, "udbytte/success.html")
        self.assertEqual(U1A.objects.count(), 1)
        self.assertEqual(U1AItem.objects.count(), 3)
        items = U1AItem.objects.order_by("id")
        self.assertEqual(items[0].navn, "Testperson Foobar")
        self.assertEqual(items[0].cpr_cvr_tin, "1111111111")
        self.assertEqual(items[0].adresse, "Testvej 1")
        self.assertEqual(items[0].postnummer, "1234")
        self.assertEqual(items[0].by, "Testby")
        self.assertEqual(items[0].land, "GL Greenland")
        self.assertEqual(items[0].udbytte, Decimal(1200))

        self.assertEqual(items[1].navn, "Tester Testersen")
        self.assertEqual(items[1].cpr_cvr_tin, "2222222222")
        self.assertEqual(items[1].adresse, "Testvej 1")
        self.assertEqual(items[1].postnummer, "12 34")
        self.assertEqual(items[1].by, "Testby")
        self.assertEqual(items[1].land, "GL Greenland")
        self.assertEqual(items[1].udbytte, Decimal(1100))

        self.assertEqual(items[2].navn, "Test Noname")
        self.assertEqual(items[2].cpr_cvr_tin, "3333333333")
        self.assertEqual(items[2].adresse, "Testvej 1")
        self.assertEqual(items[2].postnummer, "DK-1234")
        self.assertEqual(items[2].by, "Testby Vest")
        self.assertEqual(items[2].land, "GL Greenland")
        self.assertEqual(items[2].udbytte, Decimal(400))

        # Verify mocked methods
        mock_render_filled_form.assert_called_once()
        mock_send_mail_to_submitter.assert_called_once_with(b"PDF_DATA")
        mock_get_csv.assert_called_once()
        mock_save_files.assert_called_once()
        mock_send_mail_to_office.assert_called_once_with(b"CSV_DATA", b"PDF_DATA")

    @override_settings(EMAIL_OFFICE_RECIPIENT="office@example.com")
    @patch(
        "udbytte.views.UdbytteCreateView.render_filled_form", return_value=b"PDF_DATA"
    )
    @patch("udbytte.views.UdbytteCreateView.send_mail_to_submitter")
    @patch("udbytte.views.UdbytteCreateView.get_csv", return_value=b"CSV_DATA")
    @patch("udbytte.views.UdbytteCreateView.save_files")
    @patch("udbytte.views.UdbytteCreateView.send_mail_to_office")
    def test_upload_error(
        self,
        mock_send_mail_to_office: MagicMock,
        mock_save_files: MagicMock,
        mock_get_csv: MagicMock,
        mock_send_mail_to_submitter: MagicMock,
        mock_render_filled_form: MagicMock,
    ):

        # Set up mock session data
        session = self.client.session
        session["user_info"] = {"cpr": "1234567890"}
        session.save()

        # Create form data
        form_data = {
            "navn": "Test User",
            "email": "test@example.com",
            "revisionsfirma": "Test Firm",
            "virksomhedsnavn": "Test Company",
            "cvr": "12345678",
            "regnskabsår": "2023",
            "u1_udfyldt": "0",
            "udbytte": Decimal("1337.00"),  # Use Decimal to match actual call
            "noter": "Test notes",
            "by": "Test City",
            "dato": date(2023, 1, 1),  # Use datetime.date to match actual call
            "dato_vedtagelse": date(
                2023, 1, 1
            ),  # Use datetime.date to match actual call
            "underskriftsberettiget": "Authorized User",
            "use_file": "1",
            "file": File(open("udbytte/tests/resources/test_with_error.xlsx", "rb")),
        }

        request = self.factory.post("/udbytte/", {**form_data})
        request.session = session
        request.user = MagicMock()
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ["udbytte/form.html"])
        self.assertEqual(U1A.objects.count(), 0)
        self.assertEqual(U1AItem.objects.count(), 0)
        response.render()
        self.assertIn("udbytte.split_postcode_fail", str(response.content))

        form_data["file"] = File(
            open("udbytte/tests/resources/test_with_error_2.xlsx", "rb")
        )
        request = self.factory.post("/udbytte/", {**form_data})
        request.session = session
        request.user = MagicMock()
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ["udbytte/form.html"])
        self.assertEqual(U1A.objects.count(), 0)
        self.assertEqual(U1AItem.objects.count(), 0)
        response.render()
        self.assertIn("udbytte.header_fail", str(response.content))

        form_data["file"] = File(open("udbytte/tests/resources/test_empty.xlsx", "rb"))
        request = self.factory.post("/udbytte/", {**form_data})
        request.session = session
        request.user = MagicMock()
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ["udbytte/form.html"])
        self.assertEqual(U1A.objects.count(), 0)
        self.assertEqual(U1AItem.objects.count(), 0)
        response.render()
        self.assertIn("udbytte.no_data", str(response.content))
