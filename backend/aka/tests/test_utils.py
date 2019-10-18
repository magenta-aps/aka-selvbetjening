import datetime

from aka.utils import datefromstring, datetostring
from django.test import SimpleTestCase


class BasicTestCase(SimpleTestCase):
    def setUp(self):
        pass

    # Test module utils.
    # -------------------
    def test_utils_1(self):
        datestring = '2018-05-13'
        dd = datefromstring(datestring)
        self.assertTrue(type(dd) is datetime.datetime)
        self.assertEqual(dd.year, 2018)
        self.assertEqual(dd.month, 5)
        self.assertEqual(dd.day, 13)

    def test_utils_2(self):
        try:
            datefromstring('2018-20-20')
            self.fail('Failed to catch ValueError.')
        except ValueError:
            self.assertTrue(True)

    def test_utils_3(self):
        try:
            datefromstring('2018-02-50')
            self.fail('Failed to catch ValueError.')
        except ValueError:
            self.assertTrue(True)

    def test_utils_4(self):
        try:
            datefromstring('2018-02')
            self.fail('Failed to catch ValueError.')
        except ValueError:
            self.assertTrue(True)

    def test_utils_5(self):
        datestring1 = '2018-02-01'
        date = datefromstring(datestring1)
        datestring2 = datetostring(date)
        self.assertEqual(datestring1, datestring2)
