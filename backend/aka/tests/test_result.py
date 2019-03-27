from django.test import SimpleTestCase
from aka.helpers.result import Success, Error 
from aka.helpers.validation import validateRequired


class ResultTestCase(SimpleTestCase):
    def setUp(self):
        self.s1 = Success("S1")
        self.s2 = Success("S2")

        self.e1 = Error("TEST-UNKNOWN-ID")
        self.e2 = Error("TEST-UNKNOWN-ID2", field="something")
        self.e3 = Error("required_field")
        self.e4 = Error("required_field", field="something")

    def test_success(self):
        ''' Test Success always is true
        '''
        self.assertTrue(self.s1.status)

    def test_error(self):
        ''' Test error always is false
        '''
        self.assertFalse(self.e1.status)
        self.assertFalse(self.e2.status)
        self.assertFalse(self.e3.status)
        self.assertFalse(self.e4.status)

    def test_append(self):
        ''' Test append works correctly
        '''

        self.assertTrue(self.s2.append(self.s1).status)

        # This property should not be used, but we still test that is does
        # not change if you need to work with the data, "andThen" should be
        # used directly on the Success object,
        # eg: Success(x).append(Success(y).andThen(f))
        self.assertEqual(self.s1.append(self.s2).value, "S2")

        e5 = self.e1.append(self.e2)

        self.assertFalse(e5.status)
        self.assertEqual(e5.errors, [{'da': "TEST-UNKNOWN-ID",
                                      'kl': "TEST-UNKNOWN-ID"}])
        self.assertEqual(e5.fieldErrors,
                         {'something': {'da': "TEST-UNKNOWN-ID2",
                                        'kl': "TEST-UNKNOWN-ID2"}})

        # Appending a Success to an Error does not change the error
        self.assertEqual(e5.append(self.s1), e5)

        # Appending an Error to an Success should equal the Error
        self.assertEqual(self.s1.append(e5), e5)

        # Appending Errors extends the error list
        l1 = e5.errors + self.e3.errors
        self.assertEqual(e5.append(self.e3).errors, l1)

        # Appending Errors extends the fieldErrors dict
        d1 = dict(e5.fieldErrors)
        d1.update(self.e4.fieldErrors)
        self.assertEqual(e5.append(self.e4).fieldErrors, d1)

    def test_map(self):
        ''' Test map works correctly
        '''
        def f1(x): return x+"f1-applied"

        def identity(x): return x

        # map with identity never changes anything
        self.assertEqual(self.e1, self.e1.map(identity))
        self.assertEqual(self.s1, self.s1.map(identity))

        # map on an Error does not change it
        self.assertEqual(self.e1, self.e1.map(f1))

        # map on a Success changes the Success
        self.assertNotEqual(self.s1, self.s1.map(f1))
        # map on a Success cannot change make it into and Error
        self.assertTrue(self.s1.map(f1).status)

    def test_andThen(self):
        ''' Test andThen works correctly
        '''
        def f1(x): return Success(x)

        def f2(x): return Error("TEST-UNKNOWN-ID3")

        def f3(x): return Success('NEW VALUE')

        # andThen does not change an Error
        self.assertEqual(self.e1, self.e1.andThen(f1))

        # andThen only changes the value.
        # the function given here returns a new Success, with the same value
        # they should therefore be equal
        self.assertEqual(self.s1, self.s1.andThen(f1))

        # andThen changes a Success
        self.assertNotEqual(self.s1, self.s1.andThen(f2))
        self.assertNotEqual(self.s1, self.s1.andThen(f3))

        # andThen can transform a Success to and Error
        self.assertFalse(self.s1.andThen(f2).status)
        self.assertTrue(self.s1.andThen(f3).status)

    def test_either(self):
        ''' Test either works correctly
        '''
        # Success.either does not change the Success
        self.assertEqual(self.s1, self.s1.either(self.s2, self.e1))
        self.assertEqual(self.s1, self.s1.either(self.e2, self.e1))

        # Either a Success to an Error does not change the Success
        self.assertEqual(self.s1, self.e1.either(self.s1, self.e1))

        # Either an Error to an Error returns an Error
        self.assertEqual(self.e3, self.e1.either(self.e2, self.e3))

    def test_validateRequired(self):
        required = ['test1']
        required2 = ['test1', 'test4']

        requestS1 = {'test1': 'S1-test1'}
        requestS2 = {'test1': 'S2-test1', 'test2': 'S2-test2'}
        requestS3 = {'test2': 'S3-test2', 'test1': 'S3-test1'}
        requestS4 = {'test4': 'S4-test4', 'test2': 'S4-test2',
                     'test1': 'S4-test1'}

        requestE1 = {'test2': 'E1-test2'}
        requestE2 = {}
        requestE3 = {'test2': 'E3-test2', 'test3': 'E3-test3'}
        requestE4 = {'test2': 'E4-test2', 'test4': 'E4-test4',
                     'test3': 'E4-test3'}

        # Works with valid data
        self.assertTrue(validateRequired(required, requestS1).status)
        # Works when non-required fields also exists
        self.assertTrue(validateRequired(required, requestS2).status)
        # Works when required field is not first
        self.assertTrue(validateRequired(required, requestS3).status)
        # Returns Success when both required fields are present
        self.assertTrue(validateRequired(required2, requestS4).status)

        # Returns Error when only a non-required field exists
        self.assertFalse(validateRequired(required, requestE1).status)
        self.assertFalse(validateRequired(required2, requestE1).status)
        # Returns Error with empty dict
        self.assertFalse(validateRequired(required, requestE2).status)
        self.assertFalse(validateRequired(required2, requestE2).status)
        # Returns Error when required field is not present
        self.assertFalse(validateRequired(required, requestE3).status)
        self.assertFalse(validateRequired(required2, requestE3).status)
        # Returns Error when only one out of 2 required fields are present
        self.assertFalse(validateRequired(required2, requestE4).status)
