
System architecture
===================

An HTTP request comes in from a caller, which is any component that calls our REST backend.

The request goes through 4 states, and ends in one of two end states:

  * 1: Received by the backend/the endpoint called.
  * 2: Converted to internal representation.
  * 3: Validated.
  * 4: Sent (to Prisme).
  * 5: FAIL - if any error occurs. End state.
  * 6: OK - no errors occur. End state.

The 3 primary transitions are:

1 to 2:

  Conversion of the request, including any file(s).

  Currently this is done by the base class, JSONRestView.

2 to 3:

  Validation of the request.

3 to 4:

  Sending data to (and receiving from?) Prisme.

On any error in one of these transitions, we go to state 5, and if no errors occurred, we transition to state 6.
Both end states result in an HTTP response being sent to the caller. In case Django crashes, a code 500 is sent to
the caller, but that is handled for us.

.. figure:: img/backend-state-diagram.png

The caller is expected to be our own frontend, and in order to minimise risk,
we use 1 JSONSchema for each form.
This schema is communicated to the frontend, so that form data can be validated.
The same schema is used in the backend for a second validation. The second validation is made, because we cannot guarantee that data comes from our own frontend, i.e. anyone can post data via curl or Postman.
