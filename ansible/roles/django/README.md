Django
======

Installs python, pip, virtualenv and Django

Usage
-----

Requirements
------------

Must be run against a `apt` capable system.

Role Variables
--------------
| Variable         | Default Value |Purpose                                |
|------------------|---------------|---------------------------------------|
| `django_version` |`< 2.0`        | Specifiy the version of django to use |

Example Playbook
----------------

    - hosts: all
      roles:
         - django

License
-------

MPLv2

Author Information
------------------

Jakob Rydhof 
