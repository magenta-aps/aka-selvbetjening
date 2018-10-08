# Simple makefile to easily access some functionality
DJANGO 	= cd backend && python3 manage.py


.PHONY : runserver documentation makemigrations

# Run the server and make it assecible to the host machine
runserver : 
	$(DJANGO) runserver 0.0.0.0:8000

makemigrations : 
	$(DJANGO) makemigrations

documentation : 
	make -C doc -f Makefile html
