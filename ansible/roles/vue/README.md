vue
======

Installs nodejs, npm and vue

Usage
-----



Requirements
------------

Must be run against a `apt` capable system.

Role Variables
--------------

- `npm_path`(required): specifies the project folder where node will be used(the path for the package.json, etc.)


Example Playbook
----------------
    

    - hosts: all
      vars: 
        npm_path: /vagrant/frontend
      roles:
         - vue

License
-------

MPLv2

Author Information
------------------

Jakob Rydhof 
