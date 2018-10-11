from django.test import TestCase
from django.core.files.uploadedfile import UploadedFile
from akasite.rest.validation import JsonValidator
import json


# Create your tests here.
class BasicTestCase(TestCase):
    def setUp(self):
        pass

    # Test module JsonValidator.
    # -------------------------- 
    def test_Validator_1(self):
        schema = {
            "type" : "object",
            "properties" : {
                "price" : {"type" : "number"},
                "name" : {"type" : "string"},
                "year" : {"type" : "number"},
            },
            "required": ["price", "name", "year"],
        }
        valid = JsonValidator(schema)
        self.assertTrue(type(valid) is JsonValidator)

        jsonOK =   {"name" : "Eggs", "price" : 34.99, "year": 2018}
        self.assertTrue(valid.valid(jsonOK))

    def test_Validator_2(self):
        schema = {
            "type" : "object",
            "properties" : {
                "price" : {"type" : "number"},
                "name" : {"type" : "string"},
                "year" : {"type" : "number"},
            },
            "required": ["price", "name", "year"],
        }
        valid = JsonValidator(schema)
        self.assertTrue(type(valid) is JsonValidator)

        jsonFAIL = {"name" : "Eggs", "price" : 217.00}
        self.assertFalse(valid.valid(jsonFAIL))

    def test_Validator_3(self):
        schema = {
            "type" : "object",
            "properties" : {
                "price" : {"type" : "number"},
                "name" : {"type" : "string"},
                "year" : {"type" : "number"},
            },
            "required": ["price", "name", "year"],
        }
        valid = JsonValidator(schema)
        self.assertTrue(type(valid) is JsonValidator)

        jsonFAIL = {"name" : "Eggs", "price" : "NaN"}
        self.assertFalse(valid.valid(jsonFAIL))
