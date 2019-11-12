from unittest.mock import patch


class TestMixin(object):

    def mock_soap(self, method):
        soap_patch_1 = patch(method)
        mock = soap_patch_1.start()
        self.addCleanup(soap_patch_1.stop)
        return mock

    @staticmethod
    def get_file_contents(filename):
        with open(filename, "r") as f:
            return f.read()

    def compare(self, a, b, path):
        self.assertEqual(type(a), type(b), f"mismatch on {path}, different type {type(a)} != {type(b)}")
        if isinstance(a, list):
            self.assertEqual(len(a), len(b), f"mismatch on {path}, different length {len(a)} != {len(b)}")
            for index, item in enumerate(a):
                self.compare(item, b[index], f"{path}[{index}]")
        elif isinstance(a, dict):
            self.compare(a.keys(), b.keys(), f"{path}.keys()")
            for key in a:
                self.compare(a[key], b[key], f"{path}[{key}]")
        else:
            self.assertEqual(a, b, f"mismatch on {path}, different value {a} != {b}")
