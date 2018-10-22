from django.test import TestCase
from django.test import Client
from django.conf import settings
import json
import logging
import os


# Create your tests here.
class BasicTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.c = Client()
        self.url = '/filupload'

    def tearDown(self):
        files = os.listdir(settings.MEDIA_URL)
        for file in files:
            os.remove(os.path.join(settings.MEDIA_URL, file))

    def checkReturnValIsJSON(self, response):
        try:
            charset = response.charset
            json.dumps(json.loads(response.content.decode(charset)), indent=4)
        except json.decoder.JSONDecodeError:
            self.fail('Did not get JSON back.')

    def test_Get_Fileupload(self):
        response = self.c.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.checkReturnValIsJSON(response)

    # Legal content-type, and some formdata.
    def test_Post_fileupload_1(self):
        testfilename = 'akasite/tests/file4test.csv'
        with open(testfilename) as fp:
            response = self.c.post(self.url,
                                   {'formfelt1': 'indhold, ff1',
                                    'formfelt2': 'indhold, ff2',
                                    'attachment': fp},
                                   **{'HTTP_X_AKA_BRUGER': 'Otto'})
        self.assertEqual(response.status_code, 200)
        self.checkReturnValIsJSON(response)

    # Illegal content-type.
    def test_Post_fileupload_2(self):
        rawfiledata = '123;6555;"Michael Neidhardt";"København Ø";;;\n'
        rawfiledata += '768;098543;"Palle;peter";Ferênc Gülsen";;;'
        ctstring = 'application/json; charset='
        response = self.c.post(self.url,
                               content_type=ctstring,
                               data=rawfiledata,
                               **{'HTTP_X_AKA_BRUGER': 'Otto'})
        self.assertEqual(response.status_code, 400)
        self.checkReturnValIsJSON(response)

    # If using multipart/form-data, and boundarystring is missing,
    # Django crashes with error 500.
    # Is this intentional?
