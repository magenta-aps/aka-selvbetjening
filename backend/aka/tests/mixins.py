from unittest.mock import patch


class TestMixin(object):

    def mock(self, method):
        patch_object = patch(method)
        mock_object = patch_object.start()
        self.addCleanup(patch_object.stop)
        return mock_object

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
