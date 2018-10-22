from django.test import TestCase
from akasite.rest.utils import AKAUtils
import json
import datetime

# Create your tests here.
class BasicTestCase(TestCase):
    def setUp(self):
        pass

    # Test module utils.
    # -------------------
    def test_utils_1(self):
        datestring = '20180513'
        dd = AKAUtils.datefromstringYMD(datestring)
        self.assertTrue(type(dd) is datetime.datetime)
        self.assertEqual(dd.year, 2018)
        self.assertEqual(dd.month, 5)
        self.assertEqual(dd.day, 13)

    def test_utils_2(self):
        try:
            AKAUtils.datefromstringYMD('20182020')
            self.fail('Failed to catch ValueError.')
        except ValueError:
            self.assertTrue(True)

    def test_utils_3(self):
        try:
            AKAUtils.datefromstringYMD('20180250')
            self.fail('Failed to catch ValueError.')
        except ValueError:
            self.assertTrue(True)
