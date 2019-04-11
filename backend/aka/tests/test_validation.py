from django.test import SimpleTestCase
from aka.helpers.result import Success, Error 
from aka.helpers.validation import validateRequired
from datetime import date


class ValidationTestCase(SimpleTestCase):
    def test_validateRequired(self):
        self.assertTrue(validateRequired(['1'], {'1':1}).status)
        self.assertFalse(validateRequired(['1'], {'2':2}).status)
