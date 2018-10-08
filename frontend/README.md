# Building the AKA frontend

The AKA web frontend is a single page javascript application built with VUEJS.
Read the instructions below to develop and build the web frontend


## Getting started

*Check that your environment has node and npm installed.* 
You can check this by running `node --version` and `npm --version`. This codebase is designed to run within a Vagrant virtual machine. So you might want to run your npm commands from inside virtual machine. 

Then, from the `/frontend` directory, run
```
npm update
npm install
```

After fetching some npm packages, your project should be set up and ready to build.


## Building the javascript bundle

To build the frontend javascript bundle, run
```
npm run build
```

Your new build is a javascript file, `/fontend/assets/js/aka.js`


## Seeing it work in a browser

From the `/vagrant` folder within the virtual machine, run `make runserver`
Then browse to `localhost:8000/index` or `localhost:8000/static/index.html` to see your code in action.
