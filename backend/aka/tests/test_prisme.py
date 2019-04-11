from django.test import TestCase
from aka.helpers.prisme import Prisme
from aka.helpers.utils import AKAUtils


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
        rn = self.p.getRentenota(('2019','01'))
        self.assertTrue(rn.status)
