import logging
import os

from django.test import TransactionTestCase
from aka.tests.mixins import TestMixin
from lxml import etree


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
                'maindir': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'fordringshaverkonto'),
                'subdir': '{cvr}.*',
                'files': '*'
            }
        }):
            response = self.client.get(self.url)
            root = etree.fromstring(response.content, etree.HTMLParser())
            rows = root.xpath("//table[@class='folder-table']//tbody//tr")
            self.assertEqual(5, len(rows))
            data = []
            for row in rows:
                data.append([cell.text for cell in row.xpath("td")])
            self.assertEqual([
                ['sub', '1 elementer', 'Mappe'],
                ['test1.txt', '20 B', 'txt'],
                ['test2.txt', '26 B', 'txt'],
                ['test3.txt', '18 B', 'txt'],
                ['test5.txt', '18 B', 'txt']
            ], data)

