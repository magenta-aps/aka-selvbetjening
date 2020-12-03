.. _structure:

Structure
=========

The following document is intended to describe the structure guidelines for the project.

Top Folder structure:
---------------------

- **backend**               (The Django Project)

  - **aka**                 (The Django Application)

    - **rest**              (The Django views for the REST interface)
    
    - **helpers**           (This contains auxiliary python modules)

    - **tests**             (This is where the tests are)

    - **htmlviews.py**      (This is the python file serving the frontend)

    - **settings.py**       (The Django settings file)

    - **local_settings.py** (A REQUIRED settings file for the project, that is not part of git)

      In order to make onboarding easier, this file is created by :code:`make`, whenever it
      is required.

    - **urls.py**           (The route definition for the backend)

      the frontend does it's own routing, on paths starting with :code:`/index#/`

  - **openid**              (The folder for the openid login-integration)

  - **uploadedfiles**       (This folder is required, but not part og git)

    The folder is used to place files uploaded by users
    
- **frontend**              (The Vue project)

  - **dist**                (Contains the files to be served staticly by Django)  

    - **index.html**        (The entry point for the Vue app)
  
  - **src**                 (The Vue source code)

- **shared**                (Resources shared between frontend and backend)

- **doc**                   (The Sphinx documentation)

  The structure for the documentation folder should follow the structure 
  of the documentation site. Therefore an `index.rst` file exists, which includes
  all files from the `index/`-folder, and a `development.rst` which introduces
  one to development, and then includes all files in `development/`.

- **vagrant**               (Virtual machine setup for development)

  - **...**

- **ansible**               (Configuration of development and production machines)

  - **...**

- **makefile-utils**        (Utility scripts for the makefile)
