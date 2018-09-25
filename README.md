Django Vangrant-Ansible Project template
========================================

Basic template cloned from github.com:magenta-aps/vagrant-ansible-example.git

For the Windows equivalent, see [here](https://github.com/magenta-aps/vagrant-ansible-example-windows)
## Requirements:

### Development:
- Vagrant is needed to spin up a virtualized enviroment.  
- Virtualbox see [Magenta Vagrant](https://github.com/magenta-aps/vagrant/blob/master/README.md) for more info.

## Setup:

### Important files:
`doc/requirements.txt`: the python requirement file, generated with pip freeze. All packages will be installed by provisioning.




## Usage:
### Development:
From the vagrant folder:  
`vagrant up` will spin up a virtual machine and provision it.  
`vagrant ssh` can then be used to ssh into the machine.

Everything in this(the root folder of this project) folder will be shared with the VM and accessible in the  `/vagrant` folder inside the VM.

From `/vagrant` in the virtual machine:  
running `make runserver` will start up the django server, and it should be assecible from your host machine on port localhost:8000  
`make documentation` will run sphinx and generate documentation. accessible as static html files in `vagrant/doc/_build/html`


### Production:


### Running specific playbooks:

By default the `default.yml` playbook is run, but any playbook can be run, by
changing the `PLAYBOOK` environmental variable before running `vagrant provision`,
as done by:

    PLAYBOOK=demo.yml vagrant provision


