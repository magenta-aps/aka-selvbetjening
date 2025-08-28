from unittest.mock import patch

from aka.clients.prisme import (
    PrismeCvrCheckRequest,
    PrismeCvrCheckResponse,
    PrismeHttpException,
)
from zeep.exceptions import TransportError


class TestMixin(object):

    def process_service_mock(self, prisme_request, *args):
        if self.prisme_http_error is not None:
            raise PrismeHttpException(
                TransportError(status_code=self.prisme_http_error)
            )
        if self.prisme_exception is not None:
            raise self.prisme_exception
        if prisme_request.__class__ == PrismeCvrCheckRequest:
            return [
                PrismeCvrCheckResponse(
                    None, "<FujClaimant><ClaimantId>32SE</ClaimantId></FujClaimant>"
                )
            ]
        for classname, response in self.prisme_return.items():
            if prisme_request.__class__.__name__ == classname:
                if type(response) is not list:
                    response = [response]
                return response

    def setUp(self):
        self.prisme_http_error = None
        self.prisme_exception = None
        self.prisme_return = {}
        self.url = "/inkassosag/"
        self.service_mock = self.mock("aka.clients.prisme.Prisme.process_service")
        self.service_mock.side_effect = self.process_service_mock

        self.dafomock = self.mock("aka.clients.dafo.Dafo.lookup_cvr")
        self.dafomock.return_value = {
            "navn": "Testfirma",
            "adresse": "Testvej 42",
            "postnummer": "1234",
            "bynavn": "Testby",
            "landekode": "DK",
        }

    def mock(self, method):
        patch_object = patch(method)
        mock_object = patch_object.start()
        return mock_object

    @staticmethod
    def get_file_contents(filename):
        with open(filename, "r") as f:
            return f.read()

    def compare(self, a, b, path):
        self.assertEqual(
            type(a),
            type(b),
            f"mismatch on {path}, different type {type(a)} != {type(b)}",
        )
        if isinstance(a, list):
            self.assertEqual(
                len(a),
                len(b),
                f"mismatch on {path}, different length {len(a)} != {len(b)}",
            )
            for index, item in enumerate(a):
                self.compare(item, b[index], f"{path}[{index}]")
        elif isinstance(a, dict):
            self.compare(a.keys(), b.keys(), f"{path}.keys()")
            for key in a:
                self.compare(a[key], b[key], f"{path}[{key}]")
        else:
            self.assertEqual(a, b, f"mismatch on {path}, different value {a} != {b}")
