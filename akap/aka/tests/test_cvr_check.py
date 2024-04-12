from aka.clients.prisme import PrismeCvrCheckRequest, PrismeCvrCheckResponse
from aka.tests.mixins import TestMixin
from django.test import SimpleTestCase
from xmltodict import parse as xml_to_dict


class BasicTestCase(TestMixin, SimpleTestCase):
    # PRISME INTERFACE TESTS ###

    def test_check_cvr_request_parse(self):
        request = PrismeCvrCheckRequest("12345678")
        self.compare(
            xml_to_dict(
                self.get_file_contents("aka/tests/resources/cvrcheck_request.xml")
            ),
            xml_to_dict(request.xml),
            "",
        )

    def test_check_cvr_response_parse(self):
        response = PrismeCvrCheckResponse(
            None, self.get_file_contents("aka/tests/resources/cvrcheck_response.xml")
        )
        self.assertEqual(2, len(response.claimant_id))
        self.assertEqual("35SKATDK", response.claimant_id[0])
        self.assertEqual("35BIDRAGDK", response.claimant_id[1])
