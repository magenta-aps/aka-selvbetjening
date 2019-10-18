import json

from django.test import SimpleTestCase


class ErrorsIntegrityTestCase(SimpleTestCase):

    """All errormessages should be available in both danish an greenlandic
    """
    def setUp(self):
        jsonfile = open('../shared/errors.json', 'r')
        self.jsonDict = json.loads(jsonfile.read())

    def test_both_languages(self):
        for (k, v) in self.jsonDict.items():
            self.assertTrue('da' in v, msg=k + ' does not contain "da"')
            self.assertTrue('kl' in v, msg=k + ' does not contain "kl"')
