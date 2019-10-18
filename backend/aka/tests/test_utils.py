import datetime
import json

from aka.utils import ErrorJsonResponse
from aka.utils import datefromstring, datetostring
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorDict, ErrorList
from django.test import SimpleTestCase


class BasicTestCase(SimpleTestCase):
    def setUp(self):
        pass

    # Test module utils.
    # -------------------
    def test_utils_1(self):
        datestring = '2018-05-13'
        dd = datefromstring(datestring)
        self.assertTrue(type(dd) is datetime.datetime)
        self.assertEqual(dd.year, 2018)
        self.assertEqual(dd.month, 5)
        self.assertEqual(dd.day, 13)

    def test_utils_2(self):
        try:
            datefromstring('2018-20-20')
            self.fail('Failed to catch ValueError.')
        except ValueError:
            self.assertTrue(True)

    def test_utils_3(self):
        try:
            datefromstring('2018-02-50')
            self.fail('Failed to catch ValueError.')
        except ValueError:
            self.assertTrue(True)

    def test_utils_4(self):
        try:
            datefromstring('2018-02')
            self.fail('Failed to catch ValueError.')
        except ValueError:
            self.assertTrue(True)

    def test_utils_5(self):
        datestring1 = '2018-02-01'
        date = datefromstring(datestring1)
        datestring2 = datetostring(date)
        self.assertEqual(datestring1, datestring2)

    def test_error_invalid_month(self):
        response = ErrorJsonResponse.invalid_month()
        data = json.loads(response.content)
        self.assertEqual(
            "Invalid måned - skal være mellem 1 og 12",
            data['errors'][0]['da']
        )
        self.assertEqual(0, len(data['fieldErrors']))

    def test_error_future_month(self):
        response = ErrorJsonResponse.future_month()
        data = json.loads(response.content)
        self.assertEqual(
            "Ugylding måned - må ikke ligge i fremtiden",
            data['errors'][0]['da']
        )
        self.assertEqual(0, len(data['fieldErrors']))

    def test_error_dict(self):
        errors = ErrorDict()
        errors['somefield'] = ErrorList()
        errors['somefield'].extend(ValidationError('someerror').error_list)
        response = ErrorJsonResponse.from_error_dict(errors)
        self.assertEqual(400, response.status_code)
        self.assertJSONEqual(
            response.content,
            {
                "errors": [],
                "fieldErrors": {
                    "somefield": [{"da": "someerror", "kl": "someerror"}]
                }
            }
        )
