from django.test import TestCase
from django.http import HttpResponseBadRequest
from akasite.rest.base import JSONRestView, ContentTypeError
import json
import logging


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
        headerstring = 'application/json;charset=utf-8'
        ct = obj.getContenttype(headerstring)
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
        headerstring = 'application/json; charset=utf-8'
        ct = obj.getContenttype(headerstring)
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
        headerstring = 'application/json ;charset=utf-8'
        ct = obj.getContenttype(headerstring)
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
        headerstring = 'application/json ; charset=utf-8'
        ct = obj.getContenttype(headerstring)
        self.assertTrue(type(ct) is dict)
        self.assertTrue('type' in ct)
        self.assertTrue('charset' in ct)
        self.assertEqual(ct['type'], 'application/json')
        self.assertEqual(ct['charset'], 'utf-8')

    def test_contenttype_1E(self):
        '''
        Using OK headerstring.
        Test this according to the rules, as described
        here:
        https://tools.ietf.org/html/rfc7231#section-3.1.1.1
        '''
        obj = JSONRestView()
        headerstring = 'application/json ;'
        ct = obj.getContenttype(headerstring)
        self.assertTrue(type(ct) is dict)
        self.assertTrue('type' in ct)
        self.assertTrue('charset' in ct)
        self.assertEqual(ct['type'], 'application/json')

    def test_validcontenttype_1(self):
        ct = JSONRestView.CT1
        charset = 'utf-8'
        dict = {'CONTENT_TYPE': ct+';charset='+charset}
        obj = JSONRestView()
        res = obj.validContenttype(dict, ct)
        # self.assertTrue(type(res) is dict) # Why does this fail?
        self.assertTrue('type' in res)
        self.assertTrue('charset' in res)

    def test_validcontenttype_2(self):
        ct = JSONRestView.CT1
        charset = 'utf-8'
        dict = {'wrongkey': ct+';charset='+charset}
        obj = JSONRestView()
        try:
            obj.validContenttype(dict, ct)
            self.fail('Failed to catch missing CONTENT_TYPE key.')
        except ContentTypeError:
            pass

    def test_validcontenttype_3(self):
        ct = JSONRestView.CT1
        dict = {'CONTENT_TYPE': ct+';charset='}
        obj = JSONRestView()
        try:
            obj.validContenttype(dict, ct)
            self.fail('Failed to catch missing charset.')
        except ContentTypeError:
            pass

    def test_validcontenttype_4(self):
        ct = JSONRestView.CT1
        dict = {'CONTENT_TYPE': ct}
        obj = JSONRestView()
        try:
            obj.validContenttype(dict, ct, False)
        except ContentTypeError:
            self.fail('Should not fail on missing charset.')

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
