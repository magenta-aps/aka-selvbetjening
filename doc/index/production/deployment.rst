
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

Vagrant setup has also been implemented; the frontend can be deployed to a vagrant box
with the command :code:`vagrant up --provision` from the :code:`vagrant` folder

Backend
=======

The backend is a Django project, and an Ansible playbook has been created for deployment.
Deployment is achieved by issuing the command
:code:`ansible-playbook -i akaptest01, -K playbooks/deploy.yml --ask-vault-pass`
It will take whatever is in the :code:`frontend/dist` folder, as well as the backend, and
transfer it to the server, setting up dependencies, databases and configuration.
