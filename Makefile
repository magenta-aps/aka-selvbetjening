# Simple makefile to easily access some functionality

# These are simple shortcuts for commands used alot from specific places
DJANGO 	= cd backend && python3 manage.py
NPM = cd frontend && npm
FRONTEND_SOURCES = $(shell find frontend/src -type f) 
FRONTEND_PREREQUISITES = frontend/.make-updated-npm frontend/public/index.html frontend/vue.config.js $(FRONTEND_SOURCES)


# .PHONY tells make, that it is not an actual file being built
.PHONY : runserver documentation makemigrations frontend migrate test

# Run the server and make it assecible to the host machine
# .PHONY
runserver : frontend/dist/index.html  backend/aka/local_settings.py migrate
	$(DJANGO) runserver 0.0.0.0:8000

# In order to run the Django project, a local_settings.py file is required
# but this file is not supposed to be checked into git, as it contains a secret
# key, therefore it should be generated, this make-rule will generate it, if it
# does not exist.
backend/aka/local_settings.py : 
	python3 makefile-utils/gen_local_settings.py > backend/aka/local_settings.py	

# .PHONY	
test: backend/aka/local_settings.py migrate 
	-flake8 --format='%(path)s:%(row)d:%(col)d: %(code)s %(text)s' \
			--exclude=settings.py,local_settings.py,manage.py \
			backend 
	$(DJANGO) test

# .PHONY
migrate : backend/aka/local_settings.py
	$(DJANGO) migrate

# .PHONY
makemigrations : backend/aka/local_settings.py
	$(DJANGO) makemigrations

# .PHONY
documentation : 
	make -C doc -f Makefile html

# .PHONY
frontend : frontend/dist/index.html 

# FRONTEND_SOURCES checks if any files used as source files has changed, and compiles
# the frontend if it has
frontend/dist/index.html : $(FRONTEND_PREREQUISITES)
	$(NPM) run build

frontend/.make-updated-npm : frontend/package.json
	$(NPM) update
	$(NPM) install
	touch frontend/.make-updated-npm

# $@ is the target file (shared/fordringsgruppe.js)
# $< is the prerequisitte (frontend/assets/fordringsgruppe.json) 
# The second argument is the json variable name
frontend/assets/fordringsgruppe.js : shared/fordringsgruppe.json
	makefile-utils/gen_json-variable_for_frontend.sh $< groups > $@
