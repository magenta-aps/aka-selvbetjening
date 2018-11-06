from django.test import TestCase
from jsonschema import validate
import json


# JSonSchema for shared/fordringsgruppe.json
SCHEMA = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'value': {
                    'type': 'string'
                    },
                'id': {
                    'type': 'string'
                    },
                'sub_groups': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'value': {
                                'type': 'string'
                                },
                            'id': {
                                'type': 'string'
                                }
                            },
                        'required': ['value','id']
                        },
                    'minItems': 1
                    }
                },
            'required': ['value','id','sub_groups']
            }
        }

class FordringsTestCase(TestCase):
    def test_json_valid(self):
        with open('../shared/fordringsgruppe.json', 'r') as jsonfile:
            jsonDict = json.loads(jsonfile.read())
            try:
                validation = validate(jsonDict, SCHEMA)
            except Exception:
                self.fail('Validation failed.')

