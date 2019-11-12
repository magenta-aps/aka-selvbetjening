from unittest.mock import patch


class SoapTestMixin(object):
    def mock_soap(self, method):
        soap_patch_1 = patch(method)
        mock = soap_patch_1.start()
        self.addCleanup(soap_patch_1.stop)
        return mock
