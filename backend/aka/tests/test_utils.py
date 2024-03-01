import datetime

from aka.utils import datefromstring, datetostring, format_filesize
from django.test import SimpleTestCase


class BasicTestCase(SimpleTestCase):
    def setUp(self):
        pass

    # Test module utils.
    # -------------------
    def test_utils_1(self):
        datestring = "2018-05-13"
        dd = datefromstring(datestring)
        self.assertTrue(type(dd) is datetime.datetime)
        self.assertEqual(dd.year, 2018)
        self.assertEqual(dd.month, 5)
        self.assertEqual(dd.day, 13)

    def test_utils_2(self):
        try:
            datefromstring("2018-20-20")
            self.fail("Failed to catch ValueError.")
        except ValueError:
            self.assertTrue(True)

    def test_utils_3(self):
        try:
            datefromstring("2018-02-50")
            self.fail("Failed to catch ValueError.")
        except ValueError:
            self.assertTrue(True)

    def test_utils_4(self):
        try:
            datefromstring("2018-02")
            self.fail("Failed to catch ValueError.")
        except ValueError:
            self.assertTrue(True)

    def test_utils_5(self):
        datestring1 = "2018-02-01"
        date = datefromstring(datestring1)
        datestring2 = datetostring(date)
        self.assertEqual(datestring1, datestring2)

    def test_format_filesize(self):
        self.assertEqual("100 B", format_filesize(100))
        self.assertEqual("1.0 kB", format_filesize(1000))
        self.assertEqual("1.5 kB", format_filesize(1500))
        self.assertEqual("12.3 MB", format_filesize(12345678))
        self.assertEqual("12.35 MB", format_filesize(12345678, 2))
        self.assertEqual("1.0 MiB", format_filesize(1024**2, 1, False))
        self.assertEqual("1.5 MiB", format_filesize(1.5 * 1024**2, 1, False))
        self.assertEqual("1.0 GiB", format_filesize(1024**3, SI=False))
        self.assertEqual("1.0 GB", format_filesize(1000**3, SI=True))
