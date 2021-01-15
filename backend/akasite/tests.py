from django.test import TestCase
# from akasite.models import SessionOnlyUser
from django.test import Client
import requests
from lxml import html


class LoginTestCase(TestCase):
    sfc = 'Sullissivik.Federation.Cookie'

    def setUp(self):
        self.sul_address = 'http://ip.demo.sullissivik.local/login.aspx'
        self.sul_page = requests.get(self.sul_address)
        tree = html.fromstring(self.sul_page.content)
        inputs = tree.xpath('//input')

        # A dictionary containing form data to a login post
        # 'txtCPR' has value '0606606063', i.e. a valid CPR.
        self.fields = dict({
            input.name: input.value for input in inputs
        })

    def testNoSFCBeforeLogin(self):
        self.assertNotIn(self.sfc, self.sul_page.cookies)

    def testHasSFCAfterValidCPRPOST(self):
        self.assertEquals(self.fields['txtCPR'], '0606606063',
                          'Invalid input CPR')

        sul_post = requests.post(self.sul_address,
                                 data=self.fields,
                                 allow_redirects=False)

        self.assertIn(self.sfc, sul_post.cookies)

    def testHasNoSFCAfterInvalidCPRPOST(self):
        fields = self.fields
        fields['txtCPR'] = '1243142323'   # Invalid CPR
        sul_post = requests.post(self.sul_address,
                                 data=fields,
                                 allow_redirects=False)
        self.assertNotIn(self.sfc, sul_post.cookies)

    def testMissingCookieGivesRedirect(self):
        client = Client()
        response = client.get('/test/')
        self.assertEqual(302, response.status_code)

        location = response._headers.get('location')
        self.assertIn('http://ip.demo.sullissivik.local/login.aspx'
                      '?returnurl=http%3A//testserver/test/', location)

    def testLogin(self):
        sul_post = requests.post(self.sul_address,
                                 data=self.fields,
                                 allow_redirects=False)
        cookie = sul_post.cookies.get(self.sfc)

        client = Client()
        client.cookies[self.sfc] = cookie
        response = client.get('/test/')
        self.assertEqual(200, response.status_code)
