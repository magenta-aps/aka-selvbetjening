# Makefile to easily access some functionality
# Mainly used commands are:
# 	make [runserver]
# 	- Which builds frontend code, and starts the django development server
#
# 	test
# 	- Which runs flake8 on the python code and executes the tests in the backend
#
# 	documentation
# 	- Which generates the sphinx documentation (in the doc folder)
#
#	frontend 
#	- Which builds the frontend code

# These are shortcuts for commands used alot from specific places
DJANGO 	= cd backend && python3 manage.py
NPM = cd frontend && npm
FRONTEND_SOURCES = $(shell find frontend/src -type f) 
FRONTEND_PREREQUISITES = frontend/.make-updated-npm frontend/public/index.html frontend/vue.config.js $(FRONTEND_SOURCES)


# .PHONY tells make, that it is not an actual file being built
.PHONY : runserver documentation makemigrations migrate test

# Run the server and make it assecible to the host machine
# .PHONY
runserver : frontend/dist/index.html  backend/project/local_settings.py migrate
	$(DJANGO) runserver 0.0.0.0:8000

# In order to run the Django project, a local_settings.py file is required
# but this file is not supposed to be checked into git, as it contains a secret
# key, therefore it should be generated, this make-rule will generate it, if it
# does not exist.
backend/project/local_settings.py :
	python3 makefile-utils/gen_local_settings.py > backend/project/local_settings.py

# .PHONY	
test: backend/project/local_settings.py migrate
	-flake8 --format='%(path)s:%(row)d:%(col)d: %(code)s %(text)s' \
			--exclude=settings.py,local_settings.py,manage.py \
			backend 
	$(DJANGO) test

# .PHONY
migrate : backend/project/local_settings.py
	$(DJANGO) migrate

# .PHONY
makemigrations : backend/project/local_settings.py
	$(DJANGO) makemigrations

# .PHONY
documentation : 
	make -C doc -f Makefile html
