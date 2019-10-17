import logging

from django.test import TestCase, Client


class BasicTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.c = Client()
        self.url = '/nedskrivning'
