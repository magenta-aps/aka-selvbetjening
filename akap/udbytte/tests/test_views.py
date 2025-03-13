# SPDX-FileCopyrightText: 2023 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: MPL-2.0

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.template.response import TemplateResponse
from django.test import RequestFactory, TestCase, override_settings
from udbytte.models import U1A, U1AItem
from udbytte.views import UdbytteView


class UdbytteViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = UdbytteView.as_view()

    @override_settings(EMAIL_OFFICE_RECIPIENT="office@example.com")
    @patch("udbytte.views.UdbytteView.render_filled_form", return_value=b"PDF_DATA")
    @patch("udbytte.views.UdbytteView.send_mail_to_submitter")
    @patch("udbytte.views.UdbytteView.get_csv", return_value=b"CSV_DATA")
    @patch("udbytte.views.UdbytteView.save_data")
    @patch("udbytte.views.UdbytteView.send_mail_to_office")
    def test_form_valid(
        self,
        mock_send_mail_to_office: MagicMock,
        mock_save_data: MagicMock,
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
            "u1_udfyldt": False,
            "udbytte": Decimal("1337.00"),  # Use Decimal to match actual call
            "noter": "Test notes",
            "by": "Test City",
            "dato": date(2023, 1, 1),  # Use datetime.date to match actual call
            "dato_udbetaling": date(
                2023, 1, 1
            ),  # Use datetime.date to match actual call
            "underskriftsberettiget": "Authorized User",
        }

        formset_data = {
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-cpr_cvr_tin": "1234567890",
            "form-0-navn": "Item 1",
            "form-0-adresse": "Address 1",
            "form-0-postnummer": "1000",
            "form-0-by": "City A",
            "form-0-land": "Denmark",
            "form-0-udbytte": "500.00",
            "form-1-cpr_cvr_tin": "0987654321",
            "form-1-navn": "Item 2",
            "form-1-adresse": "Address 2",
            "form-1-postnummer": "2000",
            "form-1-by": "City B",
            "form-1-land": "Sweden",
            "form-1-udbytte": "837.00",
        }

        # Set up mock session data
        session = self.client.session
        session["user_info"] = {"cpr": "1234567890"}
        session.save()

        # Make the POST request for the view
        request = self.factory.post("/udbytte/", {**form_data, **formset_data})
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
        mock_send_mail_to_submitter.assert_called_once_with(
            "test@example.com", b"PDF_DATA", form_data
        )
        mock_get_csv.assert_called_once()
        mock_save_data.assert_called_once()
        mock_send_mail_to_office.assert_called_once_with(
            "office@example.com", b"CSV_DATA", b"PDF_DATA", form_data
        )
