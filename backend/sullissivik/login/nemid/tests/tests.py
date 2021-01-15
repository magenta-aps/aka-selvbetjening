import re
from http.cookiejar import Cookie
from unittest.mock import patch

from django.conf import settings
from django.template.response import TemplateResponse
from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlquote
from sullissivik.login.nemid.models import SessionOnlyUser


class LoginTestCase(TestCase):
    config = settings.NEMID_CONNECT
    sfc = config['cookie_name']
    domain = 'demo.sullissivik.local'
    outcome = None

    def setUp(self):
        pass

    def patch_sso(self, cookievalue):
        def login_response(request):
            m = re.search("<Cookie %s=(.*) for %s/>" % (self.sfc, self.domain), request.COOKIES.get(self.sfc, ''))
            if m and m.group(1) == cookievalue:
                self.outcome = True
                return SessionOnlyUser.get_user(request.session, '1234567890', 'TestUserName')
            self.outcome = False
            return SessionOnlyUser.get_user(request.session)
        patch_object = patch('sullissivik.login.nemid.nemid.NemId.authenticate')
        login_mock = patch_object.start()
        login_mock.side_effect = login_response
        self.addCleanup(patch_object.stop)

    def testMissingCookieGivesRedirect(self):
        response = self.client.get('/')
        self.assertEqual(302, response.status_code)
        location = response._headers.get('location')
        self.assertIn(reverse('aka:login') + "?back=/", location)

    def testValidCookieDoesLogin1(self):
        # Test what happens when a user shows up with a valid cookie
        cookievalue = 'here is a cookie value'
        domain = 'demo.sullissivik.local'
        cookie = Cookie(
            version=1.0, name=self.sfc, value=cookievalue,
            domain=domain, path='/',
            port=None, port_specified=None, domain_specified=None,
            domain_initial_dot=None, path_specified=None, secure=None,
            expires=None, discard=None, comment=None, comment_url=None, rest=None
        )
        self.client.cookies[self.sfc] = cookie

        self.patch_sso(cookievalue)

        response = self.client.get('/')
        self.assertEqual(200, response.status_code)
        self.assertTrue(isinstance(response, TemplateResponse))
        self.assertEqual(['index.html'], response.template_name)

    def testValidCookieDoesLogin2(self):
        # Test what happens when a user logs in through the views
        cookievalue = 'here is a cookie value'
        domain = 'demo.sullissivik.local'
        cookie = Cookie(
            version=1.0, name=self.sfc, value=cookievalue,
            domain=domain, path='/',
            port=None, port_specified=None, domain_specified=None,
            domain_initial_dot=None, path_specified=None, secure=None,
            expires=None, discard=None, comment=None, comment_url=None, rest=None
        )

        self.patch_sso(cookievalue)

        # Go to a protected page, and be redirected to login (login_response fails)
        response = self.client.get(reverse('aka:inkassosag'), follow=True)
        self.assertTrue(isinstance(response, TemplateResponse))
        self.assertEqual(['login.html'], response.template_name)
        self.assertFalse(self.outcome)

        # Have a cookie, and "be redirected" from sullissivik back to nemid login view, which accepts and redirects to the original url
        self.client.cookies[self.sfc] = cookie
        response = self.client.get(reverse('nemid:login') + "?back=" + reverse('aka:inkassosag'))
        self.assertEqual(302, response.status_code)
        location = response._headers.get('location')
        # env = self.client._base_environ()
        self.assertIn(reverse('aka:inkassosag'), location)
        self.assertTrue(self.outcome)

    def testInvalidCookieDoesRedirect(self):
        # Test what happens when a user shows up with a valid cookie
        usedcookievalue = 'here is an incorrect cookie value'
        expectedcookievalue = 'here is a correct cookie value'
        domain = 'demo.sullissivik.local'
        cookie = Cookie(
            version=1.0, name=self.sfc, value=usedcookievalue,
            domain=domain, path='/',
            port=None, port_specified=None, domain_specified=None,
            domain_initial_dot=None, path_specified=None, secure=None,
            expires=None, discard=None, comment=None, comment_url=None, rest=None
        )
        self.client.cookies[self.sfc] = cookie

        self.patch_sso(expectedcookievalue)

        response = self.client.get('/')
        self.assertEqual(302, response.status_code)
        location = response._headers.get('location')
        self.assertIn(reverse('aka:login') + "?back=/", location)

    def testValidCookieDoesRedirect2(self):
        # Test what happens when a user logs in through the views, and for some reason comes back from the SSO with an invalid cookie
        usedcookievalue = 'here is an incorrect cookie value'
        expectedcookievalue = 'here is a correct cookie value'
        domain = 'demo.sullissivik.local'
        cookie = Cookie(
            version=1.0, name=self.sfc, value=usedcookievalue,
            domain=domain, path='/',
            port=None, port_specified=None, domain_specified=None,
            domain_initial_dot=None, path_specified=None, secure=None,
            expires=None, discard=None, comment=None, comment_url=None, rest=None
        )

        self.patch_sso(expectedcookievalue)

        # Go to a protected page, and be redirected to login (login_response fails)
        response = self.client.get(reverse('aka:inkassosag'), follow=True)
        self.assertTrue(isinstance(response, TemplateResponse))
        self.assertEqual(['login.html'], response.template_name)
        self.assertFalse(self.outcome)

        # Have an invalid cookie, and "be redirected" from SSO back to nemid login view, which rejects and redirects back
        self.client.cookies[self.sfc] = cookie
        response = self.client.get(reverse('nemid:login'))
        self.assertEqual(302, response.status_code)
        location = response._headers.get('location')
        env = self.client._base_environ()
        returnurl = "http://%s%s" % (env['SERVER_NAME'], reverse('nemid:login'))
        self.assertIn("%s?%s=%s" % (self.config['login_url'], self.config['redirect_field'], urlquote(returnurl)), location)
        self.assertFalse(self.outcome)
