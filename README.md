AKA Selvbetjenningsløsninger
========================================



## Requirements:

### Development:
- Vagrant is needed to spin up a virtualized enviroment.  
- Virtualbox  
see [Vagrant README](https://github.com/magenta-aps/aka-selvbetjening/blob/develop/vagrant/README.md) for installation info.


## Setup:

### Important files:
`doc/requirements.txt`: the python requirement file. All packages will be installed by provisioning.


## Usage:

### Development:
From the vagrant folder:  
`vagrant up` will spin up a virtual machine and provision it.  
`vagrant ssh` can then be used to ssh into the machine.

Everything in this(the root folder of this project) folder will be shared with the VM and accessible in the  `/vagrant` folder inside the VM.

From `/vagrant` in the virtual machine:  
- `make runserver`: Will build everything and run the webserver. accessible at localhost:8000 on the host machine
- `make documentation`: Will generate the static html pages for the documentation. accesible in the folder `doc/_build/html/` (index.html is the frontpage)
- `make test`: Will run the test-suite.
- `make frontend`: Will build the frontend components.

For further documentation for developers, run `make documentation`
(possibly from the Virtual Machine).
Then open `doc/_build/html/index.html` in a browser, and navigate to: *Docs/Development*

### Production:

### Running specific playbooks:

By default the `default.yml` playbook is run, but any playbook can be run, by
changing the `PLAYBOOK` environmental variable before running `vagrant provision`,
as done by:

    PLAYBOOK=demo.yml vagrant provision

#### For further refference on Ansible/Vagrant setup:
Basic template cloned from github.com:magenta-aps/vagrant-ansible-example.git

For the Windows equivalent, see [here](https://github.com/magenta-aps/vagrant-ansible-example-windows)

### ansible

deply to testing (vault pass is in bitwarden) 
ansible-playbook -i akaptest01, -K playbooks/deploy.yml --ask-vault-pass