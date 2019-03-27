from django.test import SimpleTestCase
from aka.helpers.result import Success, Error 
from aka.helpers.validation import validateRequired, validateNotAfter
from datetime import date


class ValidationTestCase(SimpleTestCase):
    def test_validate_not_after(self):
        # Base cases
        self.assertTrue( validateNotAfter(date(2002,12,12), date(2003,12,12)).status )
        self.assertTrue( validateNotAfter(date(2002,12,12), date(2002,12,12)).status )
        self.assertFalse( validateNotAfter(date(2003,12,12), date(2002,12,12)).status )
        
