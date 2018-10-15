from django.test import TestCase
from django.core.files.uploadedfile import UploadedFile
from akasite.rest.validation import JsonValidator
import json


# Create your tests here.
class BasicTestCase(TestCase):
    def setUp(self):
        self.schema = {
            "type" : "object",
            "properties" : {
                "price" : {"type" : "number"},
                "name" : {"type" : "string"},
                "year" : {"type" : "number"},
            },
            "required": ["price", "name", "year"],
        }
        self.validator = JsonValidator(self.schema)
        self.assertTrue(type(self.validator) is JsonValidator)

    # Test module JsonValidator.
    # -------------------------- 
    def test_Validator_1(self):
        jsonOK =   {"name" : "Eggs", "price" : 34.99, "year": 2018}
        self.assertTrue(self.validator.valid(jsonOK))
        lasterror = self.validator.getLasterror()
        self.assertTrue(lasterror is None)

    def test_Validator_2(self):
        jsonFAIL = {"name" : "Eggs", "price" : 217.00}
        self.assertFalse(self.validator.valid(jsonFAIL))
        errmsg = self.validator.getLasterror().message
        self.assertTrue(type(errmsg) is str)

    def test_Validator_3(self):
        jsonFAIL = {"name" : "Eggs", "price" : "NaN"}
        self.assertFalse(self.validator.valid(jsonFAIL))
