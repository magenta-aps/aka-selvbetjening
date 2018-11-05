from django.test import SimpleTestCase
from akasite.rest.validation import Success, Error

class ResultTestCase(SimpleTestCase):
    def setUp(self):
        self.s1 = Success("S1")
        self.s2 = Success("S2")

        self.e1 = Error("TEST-UNKNOWN-ID")
        self.e2 = Error("TEST-UNKNOWN-ID2", field="something")
        self.e3 = Error("required_field")
        self.e4 = Error("required_field", field = "something")


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

        # This property should not be used, but we still test that is does not change
        # if you need to work with the data, "andThen" should be used directly on the
        # Success object, eg: Success(x).append(Success(y).andThen(f))
        self.assertEqual(self.s1.append(self.s2).value, "S2")

        e5 = self.e1.append(self.e2)

        self.assertFalse(e5.status)
        self.assertEqual(e5.errors,
                [{'da' : "TEST-UNKNOWN-ID", 'kl' : "TEST-UNKNOWN-ID"}])
        self.assertEqual(e5.fieldErrors,
                {'something' : { 'da' : "TEST-UNKNOWN-ID2",
                    'kl' : "TEST-UNKNOWN-ID2"}})

        # Appending a Success to an Error does not change the error
        self.assertEqual(e5.append(self.s1),e5)

        # Appending an Error to an Success should equal the Error
        self.assertEqual(self.s1.append(e5),e5)

        # Appending Errors extends the error list
        l1 = e5.errors + self.e3.errors
        self.assertEqual(e5.append(self.e3).errors,
                l1)

        # Appending Errors extends the fieldErrors dict
        d1 = dict(e5.fieldErrors)
        d1.update(self.e4.fieldErrors)
        self.assertEqual(e5.append(self.e4).fieldErrors, d1)

    def test_map():
        ''' Test map works correctly
        '''

        s1 = Error




