import logging

from django.test import SimpleTestCase


class BasicTestCase(SimpleTestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.url = '/nedskrivning'
