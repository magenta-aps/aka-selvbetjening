import json
import logging
from datetime import date

from django.test import TestCase, Client, override_settings


# Functions to test


# Create your tests here.
@override_settings(OPENID_CONNECT={'enabled': False})
class BasicTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.c = Client() #TODO not needed
        self.url = '/inkassosag?testing=0'

    def checkReturnValIsJSON(self, response):
        # TODO nasty way to check that exceptions are raise.
        try:
            charset = response.charset
            return json.loads(response.content.decode(charset))
        except json.decoder.JSONDecodeError:
            self.fail('Did not get JSON back.')

    # def test_validRequest1(self):
    #     # Contains just the required fields
    #     formData = {
    #         'fordringshaver': 'test-fordringshaver',
    #         'debitor': 'test-debitor',
    #         'fordringsgruppe': '1',
    #         'fordringstype': '1',
    #         'periodestart': date(2019, 3, 28),
    #         'periodeslut': date(2019, 3, 28),
    #         'forfaldsdato': date(2019, 3, 28),
    #         'betalingsdato': date(2019, 3, 28),
    #         'hovedstol': 100,
    #         'kontaktperson': 'Test Testersen'
    #     }
    #     response = self.c.post(self.url, formData)
    #     self.assertEqual(response.status_code, 200)
    #     self.checkReturnValIsJSON(response)
    #
    # def test_validRequest2(self):
    #     # Contains all required fields, and some more
    #     formData = {
    #         'fordringshaver': 'test-fordringshaver',
    #         'debitor': 'test-debitor',
    #         'fordringsgruppe': '1',
    #         'fordringstype': '1',
    #         'fordringshaver2': 'test-fordringshaver2',
    #         'periodestart': date(2019, 3, 27),
    #         'periodeslut': date(2019, 3, 28),
    #         'forfaldsdato': date(2019, 3, 28),
    #         'betalingsdato': date(2019, 3, 28),
    #         'hovedstol': 100,
    #         'kontaktperson': 'Test Testersen'
    #     }
    #     response = self.c.post(self.url, formData)
    #     self.assertEqual(response.status_code, 200)
    #     self.checkReturnValIsJSON(response)

    def test_invalidRequest1(self):
        # Does not contain all required fields
        formData = {
            'fordringshaver2': 'test-fordringshaver2',
            'debitor': 'test-debitor',
            'fordringsgruppe': '1',
            'fordringstype': '1',
            'periodestart': date(2019, 3, 27),
            'periodeslut': date(2019, 3, 28)
        }
        response = self.c.post(self.url, formData)
        self.assertEqual(response.status_code, 400)
        self.checkReturnValIsJSON(response)

    def test_invalidRequest2(self):
        # Test that multiple errors are recieved
        formData = {
            'fordringshaver2': 'test-fordringshaver2',
            'fordringsgruppe': '1',
            'fordringstype': '1',
            'periodestart': date(2019, 3, 27),
            'periodeslut': date(2019, 3, 28)
        }
        response = self.c.post(self.url, formData)
        self.assertEqual(response.status_code, 400)
        resp_json = self.checkReturnValIsJSON(response)
        self.assertEqual(len(resp_json['fieldErrors']), 6)


    def test_invalidRequest4(self):
        # Test fordringsgruppe and -type errors
        formData = {
            'fordringshaver2': 'test-fordringshaver2',
            'fordringshaver': 'test-fordringshaver',
            'debitor': 'test-debitor',
            'fordringsgruppe': '76',
            'fordringstype': '1',
            'periodestart': date(2019, 3, 27),
            'periodeslut': date(2019, 3, 28)
        }
        response = self.c.post(self.url, formData)
        self.assertEqual(response.status_code, 400)
        resp_json = self.checkReturnValIsJSON(response)
        self.assertEqual(
            list(resp_json['fieldErrors'].keys()),
            [
                'fordringsgruppe',
                'fordringstype',
                'hovedstol',
                'forfaldsdato',
                'betalingsdato',
                'foraeldelsesdato'
            ]
        )

    # Test multiple fields with same key
    #
    # # Legal content-type, formdata and a file.
    # def test_Post_fileupload_1(self):
    #     # Ensure filename is unique to this session,
    #     # so we can check if it was actually uploaded.
    #     filename = ''.join([
    #         random.choice('abcdefghijklmnopqrstuvwxyz0123456789')
    #         for i in range(30)
    #     ]) + '.csv'
    #     uploadfile = SimpleUploadedFile(
    #         filename,
    #         b"file_content",
    #         content_type="text/plain/"
    #     )
    #     response = self.c.post(
    #         self.url,
    #         {
    #             'fordringshaver': 'indhold/fordringshaver',
    #             'fordringsgruppe': '4',
    #             'fordringstype': '1',
    #             'debitor': 'indhold/debitor ',
    #             'attachment': uploadfile,
    #             'periodestart': date(2019, 3, 27),
    #             'periodeslut': date(2019, 3, 28),
    #             'forfaldsdato': date(2019, 3, 28),
    #             'betalingsdato': date(2019, 3, 28),
    #             'hovedstol': 100,
    #             'kontaktperson': 'Test Testersen'
    #         }
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.checkReturnValIsJSON(response)
    #     response_json = json.loads(response.content)
    #
    #     prismerequest_data = xml_to_dict(response_json['request'])
    #
    #     files = prismerequest_data['CustCollClaimTableFuj']['files']
    #     file = files['file']
    #
    #     self.assertEqual(uploadfile.name, file['Name'])
    #     self.assertEqual(base64.b64encode(b'file_content').decode("ascii"), file['Content'])
