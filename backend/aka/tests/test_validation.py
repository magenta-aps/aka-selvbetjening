from django.test import SimpleTestCase
from aka.helpers.result import Success, Error 
from aka.helpers.validation import validateRequired, validateNotAfter
from datetime import date


class ValidationTestCase(SimpleTestCase):
