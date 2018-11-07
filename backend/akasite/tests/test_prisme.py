from django.test import TestCase
from akasite.rest.prisme import Prisme
from akasite.rest.utils import AKAUtils


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
        rn = self.p.getRentenota(AKAUtils.datefromstring('2018-01-01'), AKAUtils.datefromstring('2018-02-01'))
        self.assertTrue(type(rn) is dict)
