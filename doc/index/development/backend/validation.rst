

Validation
==========

Result
======

In order to simplify validation, all validation functions should return either
a `Success` or an `Error`, theese are classes in the `validation` module, and 
are used as shown in the following example:

.. code:: python
    
    def validateFirstElement(l):
        if len(l) == 0:
            return Error("no_elements")
        else:
            return Success(l[0])

    def validateEveness(e):
        if e % 2 == 0:
            return Sucess(e)
        else: 
            return Error("uneven")
    
    def validateDoubleDigits(e):
        if e < 10:
            return Error("too_small")
        elif e >= 100:
            return Error("too_big")
        else:
            return Success(e)

    def validateNumber(e):
        # append takes another Result, and appends the Results
        return validateEveness(e).append(validateDoubleDigits(e))

    def get(request):
        validateFirstElement(request.payload
            # andThen takes a function to be executed on a Success,
            # with the value from the Success(value)
            ).andThen(validateNumber
            ).toHtmlResponse()


.. autoclass:: validation.__Result
   :members:    

