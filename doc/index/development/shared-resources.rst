

Shared Resources
================


Some resources should be shared between the frontend and the backend, to ensure consistency.

The `fordringsgruppe.json` in the `shared/` folder, is a resource shared between Python and Vue.

The way this is implemented is to have the *Makefile* generate a javascript file:
`frontend/assets/fordringsgruppe.js`, from the `fordringsgruppe.json` file, and
have the backend read the file `shared/fordringsgruppe.json`.

When the Makefile generates `frontend/assets/fordringsgruppe.js` it does some 
alterations on the Json file, and adds a variable declaration and an export.
It uses the script `makefile-utils/gen_json-variable_for_frontend.sh` to do it, 
with the following code:

.. code::
    
   makefile-utils/gen_json-variable_for_frontend.sh shared/fordringsgruppe.json groups > 
       frontend/assets/fordringsgruppe.js

In the Makefile some shortcuts is used though:

.. code::

    # $@ is the target file (shared/fordringsgruppe.js)
    # $< is the prerequisitte (frontend/assets/fordringsgruppe.json) 
    # The second argument is the json variable name
    frontend/assets/fordringsgruppe.js : shared/fordringsgruppe.json
        makefile-utils/gen_json-variable_for_frontend.sh $< groups > $@


In order to make a new shared json file you should change the following in Makefile:

- Append the name of the javascript file to :code:`FRONTEND_PREREQUISITES`
- Make a *rule* for the file, like so:
  .. code::

     *NAME OF JS FILE* : *NAME OF SHARED JSON FILE*
            makefile-utils/gen_json-variable_for_frontend.sh $< *NAME OF JS VARIABLE* > $@
   







