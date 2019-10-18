import json
import logging
from unittest.mock import patch

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import override_settings, SimpleTestCase, RequestFactory

from aka.views import RenteNotaView

from aka.clients.prisme import PrismeInterestNoteResponse


@override_settings(OPENID_CONNECT={'enabled': False})
class BasicTestCase(SimpleTestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.url = '/rentenota'
        soap_patch = patch('aka.clients.prisme.Prisme.process_service')
        self.soapmock = soap_patch.start()
        self.addCleanup(soap_patch.stop)

        dafo_patch = patch('aka.clients.dafo.Dafo.lookup_cvr')
        self.dafomock = dafo_patch.start()
        self.addCleanup(dafo_patch.stop)

    def checkReturnValIsJSON(self, response):
        try:
            charset = response.charset
            json.dumps(json.loads(response.content.decode(charset)), indent=4)
        except json.decoder.JSONDecodeError:
            self.fail('Did not get JSON back.')
    #
    # # Dates OK, invalid cvr
    def test_invalid_cvr(self):
        expected = {'errors': ['Access denied'], 'fieldErrors': []}
        for y in range(2000, 2019):
            for m in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
                response = self.client.get(self.url + f'/{y}/{m}')
                self.assertEqual(response.status_code, 403)
                self.assertEqual(json.loads(response.content), expected)

    # def test_valid_cvr(self):
    #     request_factory = RequestFactory()
    #     session_handler = SessionMiddleware()
    #     self.soapmock.return_value = [PrismeInterestNoteResponse(self.get_file_contents('aka/tests/resources/interestnote_response.xml'))]
    #     self.dafomock.return_value = {'navn': 'Test company', 'adresse': 'Test Street 42', 'postnummer': 1234, 'bynavn': 'Test town', 'landekode': 'GL'}
    #     for y in range(2000, 2019):
    #         for m in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
    #             request = request_factory.get(self.url + f'/{y}/{m}')
    #             session_handler.process_request(request)
    #             request.session['user_info'] = {'CVR': '12345678'}
    #             response = RenteNotaView.as_view()(request, y, m)
    #             self.assertEqual(response.status_code, 200)
    #             self.checkReturnValIsJSON(response)

    @staticmethod
    def get_file_contents(filename):
        with open(filename, "r") as f:
            return f.read()
