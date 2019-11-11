import json
import logging
from datetime import date
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, SimpleTestCase

from aka.clients.prisme import Prisme, PrismeClaimResponse
from aka.utils import error_definitions


@override_settings(OPENID_CONNECT={'enabled': False})
class BasicTestCase(SimpleTestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.url = '/inkassosag'
        soap_patch = patch('aka.clients.prisme.Prisme.process_service')
        self.mock = soap_patch.start()
        self.addCleanup(soap_patch.stop)

    def test_validRequest1(self):
        # Contains just the required fields
        self.mock.return_value = [PrismeClaimResponse(None, f"<CustCollClaimTableFuj><RecId>1234</RecId></CustCollClaimTableFuj>")]
        formData = {
            'fordringshaver': 'test-fordringshaver',
            'debitor': 'test-debitor',
            'fordringsgruppe': '1',
            'fordringstype': '1',
            'fordringsgruppe_id': '3',
            'periodestart': date(2019, 3, 28),
            'periodeslut': date(2019, 3, 28),
            'forfaldsdato': date(2019, 3, 28),
            'betalingsdato': date(2019, 3, 28),
            'foraeldelsesdato': date(2019, 5, 28),
            'hovedstol': 100,
            'kontaktperson': 'Test Testersen'
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'rec_id': '1234'})

    def test_validRequest2(self):
        # Contains all required fields, and some more
        self.mock.return_value = [PrismeClaimResponse(None, f"<CustCollClaimTableFuj><RecId>1234</RecId></CustCollClaimTableFuj>")]
        formData = {
            'fordringshaver': 'test-fordringshaver',
            'debitor': 'test-debitor',
            'fordringsgruppe': '1',
            'fordringstype': '1',
            'fordringsgruppe_id': '3',
            'fordringshaver2': 'test-fordringshaver2',
            'periodestart': date(2019, 3, 27),
            'periodeslut': date(2019, 3, 28),
            'forfaldsdato': date(2019, 3, 28),
            'betalingsdato': date(2019, 3, 28),
            'foraeldelsesdato': date(2019, 5, 28),
            'hovedstol': 100,
            'kontaktperson': 'Test Testersen'
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'rec_id': '1234'})

    def test_invalidRequest1(self):
        # Does not contain all required fields
        formData = {
            'fordringshaver2': 'test-fordringshaver2',
            'debitor': 'test-debitor',
            'fordringsgruppe': '1',
            'fordringstype': '1',
            'fordringsgruppe_id': '3',
            'periodestart': date(2019, 3, 27),
            'periodeslut': date(2019, 3, 28)
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 400)
        expected = {'errors': [], 'fieldErrors': {
            name: [error_definitions['required_field']]
            for name in ['fordringshaver', 'hovedstol', 'forfaldsdato', 'betalingsdato', 'foraeldelsesdato']
        }}
        self.assertEqual(
            json.loads(response.content),
            expected
        )

    def test_invalidRequest2(self):
        # Test that multiple errors are recieved
        formData = {
            'fordringshaver2': 'test-fordringshaver2',
            'fordringsgruppe': '1',
            'fordringstype': '1',
            'fordringsgruppe_id': '3',
            'periodestart': date(2019, 3, 27),
            'periodeslut': date(2019, 3, 28)
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 400)
        expected = {'errors': [], 'fieldErrors': {
            name: [error_definitions['required_field']]
            for name in ['fordringshaver', 'debitor', 'hovedstol', 'forfaldsdato', 'betalingsdato', 'foraeldelsesdato']
        }}
        self.assertEqual(
            json.loads(response.content),
            expected
        )

    def test_invalidRequest4(self):
        # Test fordringsgruppe and -type errors
        formData = {
            'fordringshaver2': 'test-fordringshaver2',
            'fordringshaver': 'test-fordringshaver',
            'debitor': 'test-debitor',
            'fordringsgruppe': '100',
            'fordringstype': '100',
            'fordringsgruppe_id': '13',
            'periodestart': date(2019, 3, 27),
            'periodeslut': date(2019, 3, 28)
        }
        response = self.client.post(self.url, formData)
        self.assertEqual(response.status_code, 400)
        expected = {'errors': [], 'fieldErrors': {
                    name: [error_definitions['required_field']]
                    for name in ['hovedstol', 'forfaldsdato', 'betalingsdato', 'foraeldelsesdato']
                }}
        expected['fieldErrors'].update({
            'fordringsgruppe': [error_definitions['fordringsgruppe_not_found']],
            'fordringstype': [error_definitions['fordringstype_not_found']]
        })
        self.assertEqual(
            json.loads(response.content),
            expected
        )

    def test_validUploadRequest2(self):
        # Contains all required fields, and some more
        self.mock.return_value = [PrismeClaimResponse(None, f"<CustCollClaimTableFuj><RecId>1234</RecId></CustCollClaimTableFuj>")]
        fp = open('aka/tests/resources/inkasso.csv', "rb")
        uploadfile = SimpleUploadedFile(
            'test.csv',
            fp.read(),
            content_type="text/csv"
        )
        fp.close()
        formData = {
            'file': uploadfile
        }
        response = self.client.post('/inkassosag/upload', formData)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [{'rec_id': '1234'}, {'rec_id': '1234'}])
