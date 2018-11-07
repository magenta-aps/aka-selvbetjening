from django.test import TestCase, Client
import unittest
import json
import logging


# Create your tests here.
class BasicTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.c = Client()
        self.url = '/inkassosag'

    def checkReturnValIsJSON(self, response):
        try:
            charset = response.charset
            return json.loads(response.content.decode(charset))
        except json.decoder.JSONDecodeError:
            self.fail('Did not get JSON back.')

    def test_validRequest1(self):
        # Contains just the required fields
        formData = {'fordringshaver': 'test-fordringshaver',
                    'debitor': 'test-debitor',
                    'fordringsgruppe': '1',
                    'fordringstype': '1'
                    }
        response = self.c.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        self.checkReturnValIsJSON(response)

    def test_validRequest2(self):
        # Contains all required fields, and some more
        formData = {'fordringshaver': 'test-fordringshaver',
                    'debitor': 'test-debitor',
                    'fordringsgruppe': '1',
                    'fordringstype': '1',
                    'fordringshaver2': 'test-fordringshaver2'
                    }
        response = self.c.post(self.url, formData)
        self.assertEqual(response.status_code, 200)
        self.checkReturnValIsJSON(response)

    def test_invalidRequest1(self):
        # Does not contain all required fields
        formData = {'fordringshaver2': 'test-fordringshaver2',
                    'debitor': 'test-debitor',
                    'fordringsgruppe': '1',
                    'fordringstype': '1'
                    }
        response = self.c.post(self.url, formData)
        self.assertEqual(response.status_code, 400)
        self.checkReturnValIsJSON(response)

    def test_invalidRequest2(self):
        # Test that multiple errors are recieved
        formData = {'fordringshaver2': 'test-fordringshaver2',
                    'fordringsgruppe': '1',
                    'fordringstype': '1'
                    }
        response = self.c.post(self.url, formData)
        self.assertEqual(response.status_code, 400)
        resp_json = self.checkReturnValIsJSON(response)
        self.assertEqual(len(resp_json['fieldErrors']), 2)

    def test_invalidRequest3(self):
        # Test fordrings-gruppe and -type errors
        formData = {'fordringshaver2': 'test-fordringshaver2',
                    'fordringshaver': 'test-fordringshaver',
                    'debitor': 'test-debitor',
                    'fordringsgruppe': '1',
                    'fordringstype': '10'
                    }
        response = self.c.post(self.url, formData)
        self.assertEqual(response.status_code, 400)
        resp_json = self.checkReturnValIsJSON(response)
        self.assertEqual(list(resp_json['fieldErrors'].keys()),
                         ['fordringstype'])

    def test_invalidRequest4(self):
        # Test fordrings-gruppe and -type errors
        formData = {'fordringshaver2': 'test-fordringshaver2',
                    'fordringshaver': 'test-fordringshaver',
                    'debitor': 'test-debitor',
                    'fordringsgruppe': '76',
                    'fordringstype': '1'
                    }
        response = self.c.post(self.url, formData)
        self.assertEqual(response.status_code, 400)
        resp_json = self.checkReturnValIsJSON(response)
        self.assertEqual(list(resp_json['fieldErrors'].keys()),
                         ['fordringsgruppe'])

    # Test multiple fields with same key

    # Legal content-type, and some formdata.
    @unittest.skip("not working atm")
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

    # If using multipart/form-data, and boundarystring is missing,
    # Django crashes with error 500.
    # Is this intentional?

    # IMPORTANT
    # We should test that files are not posted/stored on invalid form-data
