import logging

from aka.tests.mixins import TestMixin
from django.test import TransactionTestCase


class BasicTestCase(TestMixin, TransactionTestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.url = '/fordringshaverkonto/'

    # POSITIVE TESTS
