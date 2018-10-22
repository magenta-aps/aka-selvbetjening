from django.test import TestCase
from akasite.rest.prisme import Prisme
import json

# Create your tests here.
class BasicTestCase(TestCase):
    def setUp(self):
        self.p = Prisme()

    # Test module Prisme.
    # -------------------
    def test_Prisme_1(self):
        self.assertTrue(type(self.p) is Prisme)
        try:
            self.p.sendToPrisme('some data')
        except Exception:
            self.fail('Failed call to sendToPrisme')

    def test_rentenota(self):
        rn = self.p.getRentenota('01/01-18', '01/31-18')
        self.assertTrue(type(rn) is dict)
