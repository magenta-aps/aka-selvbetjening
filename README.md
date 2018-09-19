Django Vangrant-Ansible Project template
========================================

Basic template cloned from github.com:magenta-aps/vagrant-ansible-example.git

For the Windows equivalent, see [here](https://github.com/magenta-aps/vagrant-ansible-example-windows)
## Requirements:

### Development:
- Vagrant is needed to spin up a virtualized enviroment.  
- A Hypervisor(Virtualbox, lxc, libvirt, etc) see [Magenta Vagrant for more info](https://github.com/magenta-aps/vagrant/blob/master/README.md).
    - If virtualbox is not chosen, some vagrant extensions will be needed.

## Setup:



### Production:


## Usage:
### Development:
`vagrant up` will spin up a virtual machine and provision it.
`vagrant ssh` can then be used to ssh into the machine.

Everything in this folder will be shared with the VM and accessible in the  `/vagrant` folder inside the VM.

### Production:


### Running specific playbooks:

By default the `default.yml` playbook is run, but any playbook can be run, by
changing the `PLAYBOOK` environmental variable before running `vagrant provision`,
as done by:

    PLAYBOOK=demo.yml vagrant provision


