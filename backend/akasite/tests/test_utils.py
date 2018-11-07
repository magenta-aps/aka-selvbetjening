from django.test import TestCase
from akasite.rest.utils import AKAUtils
import datetime


# Create your tests here.
class BasicTestCase(TestCase):
    def setUp(self):
        pass

    # Test module utils.
    # -------------------
    def test_utils_1(self):
        datestring = '2018-05-13'
        dd = AKAUtils.datefromstring(datestring)
        self.assertTrue(type(dd) is datetime.datetime)
        self.assertEqual(dd.year, 2018)
        self.assertEqual(dd.month, 5)
        self.assertEqual(dd.day, 13)

    def test_utils_2(self):
        try:
            AKAUtils.datefromstring('2018-20-20')
            self.fail('Failed to catch ValueError.')
        except ValueError:
            self.assertTrue(True)

    def test_utils_3(self):
        try:
            AKAUtils.datefromstring('2018-02-50')
            self.fail('Failed to catch ValueError.')
        except ValueError:
            self.assertTrue(True)

    def test_utils_4(self):
        try:
            AKAUtils.datefromstring('2018-02')
            self.fail('Failed to catch ValueError.')
        except ValueError:
            self.assertTrue(True)

    def test_utils_5(self):
        datestring1 = '2018-02-01'
        date = AKAUtils.datefromstring(datestring1)
        datestring2 = AKAUtils.datetostring(date)
        self.assertEqual(datestring1, datestring2)
