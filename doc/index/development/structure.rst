
Structure
=========

The following document is intended to describe the structure guidelines for the project.

Top Folder structure:
---------------------

- **backend**       (The Django Project)

  - **aka**         (The starting point for Django, settings.py, and urls.py)

  - **akasite**     (The Django app we develop in)
    
    - **rest**      (The Django views for the REST interface)

- **frontend**      (The Vue project)

  - **assets**      (Contains the files to be served staticly by Django)  

    - **js/app.js** (The compiled Vue app)
  
  - **src**         (The Vue source code)

- **shared**        (Resources shared between frontend and backend)

- **doc**           (The Sphinx documentation)

  The structure for the documentation folder should follow the structure 
  of the documentation site. Therefore an `index.rst` file exists, which includes
  all files from the `index/`-folder, and a `development.rst` which introduces
  one to development, and then includes all files in `development/`.

- **vagrant**       (Virtual machine setup for development)

  - **...**

- **ansible**       (Configuration of development and production machines)

  - **...**

- **makefile-utils** (Utility scripts for the makefile)
