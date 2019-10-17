import json
import logging

from aka.utils import ErrorJsonResponse
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorDict, ErrorList
from django.test import TestCase


class BasicTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def checkReturnValIsJSON(self, response):
        try:
            charset = response.charset
            json.dumps(json.loads(response.content.decode(charset)), indent=4)
        except json.decoder.JSONDecodeError:
            self.fail('Did not get JSON back.')

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
