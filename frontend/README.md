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
You can see an example implementation by finding the HTML file `/frontend/dist/assets/index.html` and opening it in a browser.

Include `aka.js` in your hosted HTML.
