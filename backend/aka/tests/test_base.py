from django.core.exceptions import ValidationError
from django.test import TestCase, RequestFactory
from django.http import HttpResponseBadRequest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import json
import os
import logging
import random
from pathlib import Path
from django.forms.utils import ErrorDict, ErrorList

from aka.helpers.error import ErrorJsonResponse


class BasicTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def checkReturnValIsJSON(self, response):
        try:
            charset = response.charset
            json.dumps(json.loads(response.content.decode(charset)), indent=4)
        except json.decoder.JSONDecodeError:
            self.fail('Did not get JSON back.')

    def test_error_invalid_month(self):
        response = ErrorJsonResponse.invalid_month()
        data = json.loads(response.content)
        self.assertEqual(
            "Invalid måned - skal være mellem 1 og 12",
            data['errors'][0]['da']
        )
        self.assertEqual(0, len(data['fieldErrors']))

    def test_error_future_month(self):
        response = ErrorJsonResponse.future_month()
        data = json.loads(response.content)
        self.assertEqual(
            "Ugylding måned - må ikke ligge i fremtiden",
            data['errors'][0]['da']
        )
        self.assertEqual(0, len(data['fieldErrors']))

    def test_error_dict(self):
        errors = ErrorDict()
        errors['somefield'] = ErrorList()
        errors['somefield'].extend(ValidationError('someerror').error_list)
        response = ErrorJsonResponse.from_error_dict(errors)
        self.assertEqual(400, response.status_code)
        self.assertJSONEqual(
            response.content,
            {
                "errors": [],
                "fieldErrors": {
                    "somefield": [{"da": "someerror", "kl": "someerror"}]
                }
            }
        )

    # def test_errortext_1(self):
    #     obj = JSONRestView()
    #     txt = 'Hey ho, testing'
    #     et = json.loads(obj.errorText(txt))
    #     self.assertTrue('status' in et)
    #     self.assertTrue('message' in et)
    #     self.assertEqual(et['message'], txt)
    #
    # def test_errormessage_1(self):
    #     obj = JSONRestView()
    #     msg = 'Testing again.'
    #     exc = ContentTypeError(msg)
    #     er = obj.errorResponse(exc)
    #     self.assertTrue(type(er) is HttpResponseBadRequest)
    #     self.assertTrue(msg.lower() in er.content.decode('utf-8').lower())
    #
    # def test_cleanup_1(self):
    #     obj = JSONRestView()
    #     try:
    #         obj.cleanup()
    #     except Exception:
    #         self.fail('There should be no exception here.')
    #
    # def test_cleanup_2(self):
    #     obj = JSONRestView()
    #     tmpfile = settings.MEDIA_URL + obj.randomstring() + '.tmp'
    #     Path(tmpfile).touch()
    #     self.assertTrue(Path(tmpfile).is_file())
    #     obj.files = [{'tmpfilename': tmpfile}]
    #     obj.cleanup()
    #     self.assertFalse(Path(tmpfile).is_file())
    #
    # def simulatedFile(self):
    #     # Ensure filename is unique to this session,
    #     # so we can check if it was actually uploaded.
    #     filename = ''.join([
    #         random.choice('abcdefghijklmnopqrstuvwxyz0123456789')
    #         for i in range(30)
    #         ]) + '.csv'
    #     return SimpleUploadedFile(filename,
    #                               b"file_content",
    #                               content_type="text/plain/")
    #
    # def test_fileupload(self):
    #     '''Test upload of files.
    #     '''
    #     file1 = self.simulatedFile()
    #     file2 = self.simulatedFile()
    #     factory = RequestFactory()
    #     request = factory.post('/', {
    #                                  'field1': 'hey',
    #                                  'field2': 'ho',
    #                                  'attachment1': file1,
    #                                  'attachment2': file2,
    #                                 }
    #                            )
    #     obj = JSONRestView()
    #     response = obj.basepost(request)
    #
    #     self.assertTrue(response.status_code, 200)
    #     self.assertEqual(len(obj.files), 2)
    #     self.assertTrue(
    #             obj.files[0]['originalname'] in [file1.name, file2.name]
    #             )
    #     self.assertTrue(
    #             obj.files[1]['originalname'] in [file1.name, file2.name]
    #             )
    #     obj.cleanup()
    #
    # def test_cleanup(self):
    #     '''Test cleanup after file upload.
    #     '''
    #     file1 = self.simulatedFile()
    #     file2 = self.simulatedFile()
    #     factory = RequestFactory()
    #     request = factory.post('/', {
    #                                  'field1': 'hey',
    #                                  'field2': 'ho',
    #                                  'attachment1': file1,
    #                                  'attachment2': file2,
    #                                 }
    #                            )
    #     obj = JSONRestView()
    #     response = obj.basepost(request)
    #
    #     self.assertTrue(response.status_code, 200)
    #     self.assertEqual(len(obj.files), 2)
    #
    #     foundfiles = os.listdir(settings.MEDIA_URL)
    #     self.assertEqual(len(foundfiles), 2)
    #     obj.cleanup()
    #     foundfiles = os.listdir(settings.MEDIA_URL)
    #     self.assertEqual(len(foundfiles), 0)
