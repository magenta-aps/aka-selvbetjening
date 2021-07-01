AKA Selvbetjeningsløsninger
========================================

## Setup:
- Clone to local machine:
  - `git clone git@git.magenta.dk:gronlandsprojekter/aka-selvbetjening.git`
  - `cd aka-selvbetjening`
- Install Ansible, Virtualenv and Python3-apt:
  - `sudo apt install ansible virtualenv python3-apt`
- Create a virtual environment and enter it:
  - `virtualenv -p python3 --system-site-packages venv`
  - `source venv/bin/activate`
- Set up a local installation of AKA with ansible:
  - Install ansible python package: `pip3 install ansible `
  - Run `./deploy_local`
  - You will be asked for your local sudo password and the test-environment vault password (present in bitwarden under key "Ansible Vault Password (AKAP test deployment)")
- Connect to the Greenland VPN
- Create a tunnel to the dev server for socks, allowing you access to the Prisme development service 
  - Run `./socks.sh`
  - This will open a connection to the server that is closed if you log out of the ssh shell
- Start Django
  - Run `python3 backend/manage.py runserver`

### Development:
When the system has been set up, you don't need to recreate the virtual environment or run `deploy_local`.
Just enter the virtual environment, set up the socks connection, and run django on localhost.
Since we cannot integrate with sullissivik's login in local development, we've defined an override
CPR and CVR in settings_local.py when deployed through the localhost ansible configuration.
Development on the login solution needs to be verified on the akaptest01 server.

Eventually we may want to put the system in a docker container, but that's out of scope for now.

#### vagrant
IF you dont want to clutter your local machine with all kinds of cruft you could just use vagarnt to setup the test environment.
From the vagrant dir simply run `vagrant up`. This should start and provision the machine in a virtual machine/container.
Now you should be able to run the django project:

    cd /vagrant/backend/
    python manage.py runserver 0.0.0.0:8000
    #point your browser to http://127.0.0.0:8000

### Test:
To deploy on the test server, run: `./deploy_test`.
This will start the ansible playbook for test setup. You will be prompted for:
- your test server password
- the test vault password

### Production:
To deploy on the production server, run: `./deploy_prod`.
This will start the ansible playbook for prod setup. You will be prompted for:
- your prod server password
- the prod vault password
