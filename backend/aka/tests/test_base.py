from django.test import TestCase
from django.http import HttpResponseBadRequest
from akasite.rest.base import JSONRestView, ContentTypeError
from django.conf import settings
import json
import logging
from pathlib import Path



# Create your tests here.
class BasicTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def checkReturnValIsJSON(self, response):
        try:
            charset = response.charset
            json.dumps(json.loads(response.content.decode(charset)), indent=4)
        except json.decoder.JSONDecodeError:
            self.fail('Did not get JSON back.')

    def test_object(self):
        obj = JSONRestView()
        self.assertTrue(type(obj) is JSONRestView)

    def test_randomstring(self):
        obj = JSONRestView()
        rstr = obj.randomstring(40)
        self.assertTrue(type(rstr) is str)
        self.assertEqual(len(rstr), 40)

        rstr = obj.randomstring(60)
        self.assertTrue(type(rstr) is str)
        self.assertEqual(len(rstr), 60)

    def test_contenttype_1A(self):
        '''
        Using OK headerstring.
        Test this according to the rules, as described
        here:
        https://tools.ietf.org/html/rfc7231#section-3.1.1.1
        '''
        obj = JSONRestView()
        d = {'CONTENT_TYPE': 'application/json;charset=utf-8'}
        ct = obj.getContenttype(d)
        self.assertTrue(type(ct) is dict)
        self.assertTrue('type' in ct)
        self.assertTrue('charset' in ct)
        self.assertEqual(ct['type'], 'application/json')
        self.assertEqual(ct['charset'], 'utf-8')

    def test_contenttype_1B(self):
        '''
        Using OK headerstring.
        Test this according to the rules, as described
        here:
        https://tools.ietf.org/html/rfc7231#section-3.1.1.1
        '''
        obj = JSONRestView()
        d = {'CONTENT_TYPE': 'application/json; charset=utf-8'}
        ct = obj.getContenttype(d)
        self.assertTrue(type(ct) is dict)
        self.assertTrue('type' in ct)
        self.assertTrue('charset' in ct)
        self.assertEqual(ct['type'], 'application/json')
        self.assertEqual(ct['charset'], 'utf-8')

    def test_contenttype_1C(self):
        '''
        Using OK headerstring.
        Test this according to the rules, as described
        here:
        https://tools.ietf.org/html/rfc7231#section-3.1.1.1
        '''
        obj = JSONRestView()
        d = {'CONTENT_TYPE': 'application/json ; charset=utf-8'}
        ct = obj.getContenttype(d)
        self.assertTrue(type(ct) is dict)
        self.assertTrue('type' in ct)
        self.assertTrue('charset' in ct)
        self.assertEqual(ct['type'], 'application/json')
        self.assertEqual(ct['charset'], 'utf-8')

    def test_contenttype_1D(self):
        '''
        Using OK headerstring.
        Test this according to the rules, as described
        here:
        https://tools.ietf.org/html/rfc7231#section-3.1.1.1
        '''
        obj = JSONRestView()
        d = {'CONTENT_TYPE': 'application/json ;'}
        ct = obj.getContenttype(d)
        self.assertTrue(type(ct) is dict)
        self.assertTrue('type' in ct)
        self.assertTrue('charset' in ct)
        self.assertEqual(ct['charset'], '')
        self.assertEqual(ct['type'], 'application/json')

    def test_contenttype_1E(self):
        '''
        Using OK headerstring.
        Test this according to the rules, as described
        here:
        https://tools.ietf.org/html/rfc7231#section-3.1.1.1
        '''
        obj = JSONRestView()
        d = {'CONTENT_TYPE': 'application/json'}
        ct = obj.getContenttype(d)
        self.assertTrue(type(ct) is dict)
        self.assertTrue('type' in ct)
        self.assertTrue('charset' in ct)
        self.assertEqual(ct['charset'], '')
        self.assertEqual(ct['type'], 'application/json')

    def test_contenttype_1F(self):
        '''
        Using weird headerstring.
        Test this according to the rules, as described
        here:
        https://tools.ietf.org/html/rfc7231#section-3.1.1.1
        '''
        obj = JSONRestView()
        d = {'CONTENT_TYPE': ''}
        ct = obj.getContenttype(d)
        self.assertTrue(type(ct) is dict)
        self.assertTrue('type' in ct)
        self.assertTrue('charset' in ct)
        self.assertEqual(ct['charset'], '')
        self.assertEqual(ct['type'], '')

    def test_contenttype_1G(self):
        '''
        Using incorrect key for headerstring.
        '''
        obj = JSONRestView()
        d = {'CONTENT': 'application/json ;'}
        try:
            obj.getContenttype(d)
            self.fail('Failed to catch incorrect key in dict.')
        except ContentTypeError:
            pass

    def test_contenttypeerror_1(self):
        exc = ContentTypeError('Testing contenttypeeror.')
        self.assertTrue(type(exc) is ContentTypeError)

    def test_contenttypeerror_2(self):
        msg = 'Testing contenttypeeror.'
        exc = ContentTypeError(msg)
        self.assertEqual(exc.message, msg)

    def test_errortext_1(self):
        obj = JSONRestView()
        txt = 'Hey ho, testing'
        et = json.loads(obj.errorText(txt))
        self.assertTrue('status' in et)
        self.assertTrue('message' in et)
        self.assertEqual(et['message'], txt)

    def test_errormessage_1(self):
        obj = JSONRestView()
        msg = 'Testing again.'
        exc = ContentTypeError(msg)
        er = obj.errorResponse(exc)
        self.assertTrue(type(er) is HttpResponseBadRequest)
        self.assertTrue(msg.lower() in er.content.decode('utf-8').lower())

    def test_cleanup_1(self):
        obj = JSONRestView()
        try:
            obj.cleanup()
        except Exception:
            self.fail('There should be no exception here.')

    def test_cleanup_2(self):
        obj = JSONRestView()
        tmpfile = settings.MEDIA_URL + obj.randomstring() + '.tmp'
        Path(tmpfile).touch()
        self.assertTrue(Path(tmpfile).is_file())
        obj.files = [{'tmpfilename' : tmpfile}]
        obj.cleanup()
        self.assertFalse(Path(tmpfile).is_file())
