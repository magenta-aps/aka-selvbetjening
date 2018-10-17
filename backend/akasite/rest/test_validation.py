from django.test import TestCase
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
                'cpr': {'type': 'string',
                        'pattern': '^[0-9]{6}-[0-9]{4}$'},
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
        jsonOK = {'name': 'Eggs', 'price': 34.99, 'year': 2018}
        errors2 = JsonValidator(self.schema).validate(jsonOK)
        self.assertEqual(len(errors2), 0)

    def test_Validator_3(self):
        jsonOK = {'name': '', 'price': 34.99, 'year': 2018}
        errors = self.validator.validate(jsonOK)
        self.assertEqual(len(errors), 0)

    def test_Validator_4(self):
        jsonFAIL = {'name': 'Eggs', 'price': 217.00}
        errors = self.validator.validate(jsonFAIL)
        self.assertEqual(len(errors), 1)

    def test_Validator_5(self):
        jsonFAIL = {'name': 'Eggs', 'year': 2020}
        errors = self.validator.validate(jsonFAIL)
        self.assertEqual(len(errors), 1)

    def test_Validator_6(self):
        jsonFAIL = {'name': 'Eggs', 'price': '201.x', 'year': 'ghjghjghj'}
        errors = self.validator.validate(jsonFAIL)
        self.assertEqual(len(errors), 2)

    def test_Validator_7(self):
        jsonFAIL = {'name': 'Eggs', 'price': 201.2, 'year': 2022, 'cpr': '010190-1234' }
        errors = self.validator.validate(jsonFAIL)
        self.assertEqual(len(errors), 0)

    def test_Validator_8(self):
        jsonFAIL = {'name': 'Eggs', 'price': 201.1, 'year': 2022, 'cpr': '010190-123' }
        errors = self.validator.validate(jsonFAIL)
        self.assertEqual(len(errors), 1)

    def test_Validator_9(self):
        jsonFAIL = {'name': 'Eggs', 'price': 201.1, 'year': 2022, 'cpr': 'a10190-1234' }
        errors = self.validator.validate(jsonFAIL)
        self.assertEqual(len(errors), 1)

    def test_Validator_10(self):
        jsonFAIL = {'name': 'Eggs', 'price': 201.1, 'year': 2022, 'cpr': ' 110190-1234' }
        errors = self.validator.validate(jsonFAIL)
        self.assertEqual(len(errors), 1)

    def test_Validator_11(self):
        jsonFAIL = {'name': 'Eggs', 'price': 201.1, 'year': 2022, 'cpr': ' 110190-1234 ' }
        errors = self.validator.validate(jsonFAIL)
        self.assertEqual(len(errors), 1)
