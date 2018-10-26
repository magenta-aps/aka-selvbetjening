from jsonschema import Draft4Validator as draftValidator


class Validator():
    def __init__():
        pass


class JsonValidator(Validator):
    '''JSON Validator, using jsonschema.
    '''
    def __init__(self, schema):
        self.schema = schema
        self.lasterror = None

    def setSchema(self, schema):
        '''Set the schema used to validate against.

        :param schema: Valid jsonschema schema.
        :type schema: dict.
        '''
        self.schema = schema

    def getSchema(self):
        '''Get the current schema used.
        '''
        return self.schema

    def validate(self, object):
        '''
        Validate a JSON object.

        :param object: JSON Structure
        :type object: Python dict.
        :returns: List of 2-tuples. Each tuple
                  contains (fieldname, error message).
        '''

        v = draftValidator(self.schema)
        errors = sorted(v.iter_errors(object), key=lambda e: e.path)

        if len(errors) == 0:
            return []

        result = []

        for error in errors:
            if len(error.absolute_path) > 0:
                f = error.absolute_path[0]
            else:
                f = ''
            result.append((f, error.message))

        return result
