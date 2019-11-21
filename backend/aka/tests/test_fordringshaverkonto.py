import logging
import os

from django.test import TransactionTestCase
from aka.tests.mixins import TestMixin


class BasicTestCase(TestMixin, TransactionTestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.url = '/fordringshaverkonto'

    # POSITIVE TESTS

    def test_listing_success(self):
        session = self.client.session
        session['user_info'] = {'CVR': '12345678'}
        session.save()
        with self.settings(MOUNTS = {
            'claimant_account_statements': {
                'dir': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'fordringshaverkonto'),
                'files': '{cvr}_*'
            }
        }):
            response = self.client.get(self.url)
            print(response.content)
