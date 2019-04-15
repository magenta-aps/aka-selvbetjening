
==========
Deployment
==========

This is meant to be a guide for deploying the software to the production server.

Frontend
========

The frontend is written in Vue.js, and is placed in the :code:`frontend` folder.
The Vue project is compiled by executing :code:`npm build` from the :code:`frontend` folder.
It might be needed to run :code:`npm update; npm install` before building, if new 
packages are added.

When the frontend is compiled, the compiled javascript, html and css ends up in the
folder: :code:`frontend/dist`.
This folder should then be archived, eg. with :code:`tar -xzf frontend.tar.gz frontend/dist`
and moved to the production server, where it can be unpacked in the desired destination.

Backend
=======

The backend is a Django project.
MORE INFORMATION NEEDED

.. todo:: Write about backend deployment

