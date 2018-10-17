Validation
==========

JSONSchema is a tool for validating JSON structures.

Official docs:

https://json-schema.org/

https://pypi.org/project/jsonschema/

https://github.com/ebdrup/json-schema-benchmark

Say you have the following JSON data and a schema for validation:

.. code-block:: python

    jsondata = {
    'name': 'Michael',
    'year': 2020,
    'cpr': '123456-4321',
    'height': 190.5,
    }

    schema = {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'year': {'type': 'number'},
            'cpr': {'type': 'string', 'pattern': '^[0-9]{6}-[0-9]{4}$'},
            'height': 
        },
        'required': ['name', 'year', 'cpr'],
    }
 
This schema does basic validation, i.e. it handles data types,
content using regular expression and whether a key is required or not.

In this project, the validator is wrapped in class JsonValidator, so given the JSON data
and the schema above, you can validate the data like this:

.. code-block:: python

    from akasite.rest.validation import JsonValidator

    validator = JsonValidator(schema)
    errors = validator.validate(jsondata)

    # Now handle the result in some way.
    # len(errors) == 0 means that all is OK,
    # and len(errors) > 0 means errors were found.

See tests in the project for more info.
