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
                    'type': 'string',
                    'pattern': '^[0-9][0-9]?$'
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
                                'type': 'string',
                                'pattern': '^[0-9][0-9]?$'
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
    def setUp(self):
        try:
            jsonfile = open('../shared/fordringsgruppe.json', 'r')
            self.jsonDict = json.loads(jsonfile.read())
            try:
                validation = validate(self.jsonDict, SCHEMA)
            except Exception as e:
                self.fail('Validation failed.\n' + str(e))
        except Exception as e:
            self.fail('Could not open file.\n' + str(e))

    def test_unique_keys(self):
        # Test that all id's are unique, by comparing the length of a list to
        # the set generated byt the list, since a set only contains unique
        # value

        ids = [x['id'] for x in self.jsonDict]
        self.assertEqual(len(ids),len(set(ids)))

    def test_unique_sub_group_keys(self):
        for o in self.jsonDict:
            ids = [x['id'] for x in o['sub_groups']]
            errMsg = 'Fordringsgruppe: {0} with id: {1}, sub_groups are not '\
                     'unique.'.format(o['value'], o['id'])
            self.assertEqual(len(ids),len(set(ids)),
                    msg=errMsg)
