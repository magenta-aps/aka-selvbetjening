import jsonschema

class Validator():
    def __init__():
        pass

class JsonValidator(Validator):
    '''
    JSON Validator, using jsonschema.
    '''
    def __init__(self, schema):
        self.schema = schema

    def setSchema(self, schema):
        self.schema = schema

    def getSchema(self, schema):
        return self.schema

    def valid(self, object):
        try:
            jsonschema.validate(object, self.schema)
            return True
        except jsonschema.exceptions.ValidationError as err:
            return False
