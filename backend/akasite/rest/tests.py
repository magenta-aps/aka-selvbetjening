from django.test import TestCase
from django.core.files.uploadedfile import UploadedFile
from akasite.rest.validation import JsonValidator


# Create your tests here.
class BasicTestCase(TestCase):
    def setUp(self):
        self.schema = {
            'type': 'object',
            'properties': {
                'price': {'type': 'number'},
                'name': {'type': 'string'},
                'year': {'type': 'number'},
            },
            'required': ['price', 'name', 'year'],
        }
        self.validator = JsonValidator(self.schema)
        self.assertTrue(type(self.validator) is JsonValidator)

    # Test module JsonValidator.
    # --------------------------
    def test_Validator_1(self):
        jsonOK = {'name': 'Eggs', 'price': 34.99, 'year': 2018}
        errors = self.validator.validate(jsonOK)
        self.assertEqual(len(errors), 0)

    def test_Validator_2(self):
        jsonFAIL = {'name': 'Eggs', 'price': 217.00}
        errors = self.validator.validate(jsonFAIL)
        self.assertEqual(len(errors), 1)

    def test_Validator_3(self):
        jsonFAIL = {'name': 'Eggs', 'year': 2020}
        errors = self.validator.validate(jsonFAIL)
        self.assertEqual(len(errors), 1)

    def test_Validator_4(self):
        jsonFAIL = {'name': 'Eggs', 'price': '201.x', 'year': 'ghjghjghj'}
        errors = self.validator.validate(jsonFAIL)
        self.assertEqual(len(errors), 2)
