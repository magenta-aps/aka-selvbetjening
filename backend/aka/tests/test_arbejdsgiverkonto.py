import logging

from django.test import TestCase, Client


# Create your tests here.
class BasicTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.c = Client()
        self.url = '/arbejdsgiverkonto'
