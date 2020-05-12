import logging

from aka.tests.mixins import TestMixin
from django.test import TransactionTestCase


class BasicTestCase(TestMixin, TransactionTestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.url = '/fordringshaverkonto/'

    # POSITIVE TESTS

    def test_listing_success(self):
        session = self.client.session
        session['user_info'] = {'CVR': '12345678'}
        session.save()
        with self.settings(MOUNTS={
            'claimant_account_statements': {
                'maindir': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'fordringshaverkonto'),
                'subdir': '{cvr}.*',
                'files': '*'
            }
        }):
            response = self.client.get(self.url)
            root = etree.fromstring(response.content, etree.HTMLParser())
            self.assertIsNotNone(root)
            rows = root.xpath("//table[@class='folder-table']//tbody//tr")
            self.assertEqual(5, len(rows))
            data = []
            for row in rows:
                rowdata = []
                for cell in row.xpath("td"):
                    link = cell.xpath("a")
                    text = link[0].text if link else cell.text
                    rowdata.append(text.strip())
                data.append(rowdata)
            self.assertEqual([
                ['sub', 'Mappe', '1 elementer'],
                ['test1.txt', 'txt', '20 B'],
                ['test2.txt', 'txt', '26 B'],
                ['test3.txt', 'txt', '18 B'],
                ['test5.txt', 'txt', '18 B']
            ], data)
