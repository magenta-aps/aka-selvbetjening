from django.test import TestCase, RequestFactory
from django.http import HttpResponseBadRequest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from aka.rest.base import JSONRestView, ContentTypeError
import json
import os
import logging
import random
from pathlib import Path


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
        obj.files = [{'tmpfilename': tmpfile}]
        obj.cleanup()
        self.assertFalse(Path(tmpfile).is_file())

    def simulatedFile(self):
        # Ensure filename is unique to this session,
        # so we can check if it was actually uploaded.
        filename = ''.join([
            random.choice('abcdefghijklmnopqrstuvwxyz0123456789')
            for i in range(30)
            ]) + '.csv'
        return SimpleUploadedFile(filename,
                                   b"file_content",
                                   content_type="text/plain/")

    def test_fileupload(self):
        '''Test upload of files.
        '''
        file1 = self.simulatedFile();
        file2 = self.simulatedFile();
        factory = RequestFactory()
        request = factory.post('/', {
                                     'field1': 'hey',
                                     'field2': 'ho',
                                     'attachment1': file1,
                                     'attachment2': file2,
                                    }

                              )
        obj = JSONRestView()
        response = obj.basepost(request)

        self.assertTrue(response.status_code, 200)
        self.assertEqual(len(obj.files), 2)
        self.assertTrue(obj.files[0]['originalname'] in [file1.name, file2.name])
        self.assertTrue(obj.files[1]['originalname'] in [file1.name, file2.name])
        obj.cleanup()

    def test_cleanup(self):
        '''Test cleanup after file upload.
        '''
        file1 = self.simulatedFile();
        file2 = self.simulatedFile();
        factory = RequestFactory()
        request = factory.post('/', {
                                     'field1': 'hey',
                                     'field2': 'ho',
                                     'attachment1': file1,
                                     'attachment2': file2,
                                    }

                              )
        obj = JSONRestView()
        response = obj.basepost(request)

        self.assertTrue(response.status_code, 200)
        self.assertEqual(len(obj.files), 2)

        foundfiles = os.listdir(settings.MEDIA_URL)
        self.assertEqual(len(foundfiles), 2)
        obj.cleanup()
        foundfiles = os.listdir(settings.MEDIA_URL)
        self.assertEqual(len(foundfiles), 0)
