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


### Building the javascript bundle

To build the frontend javascript bundle for **development,** run
```
npm run dev
```

To build the frontend javascript bundle for **production,** run
```
npm run build
```

Alternatively a make-rule has been made in the root Makefile,
so from the /vagrant folder running:
```
make frontend
```
(And running make runserver, will also ensure the frontend is built)

Your new build is a collection of javascript file. For most modern browsers, your index HTML file will need to refer to `/fontend/assets/js/aka.esmodules.js` to initiate the frontend. This file will load other JS dependencies automatically.


### Seeing it work in a browser

From the `/vagrant` folder within the virtual machine, run `make runserver`
Then browse to `localhost:8000/index` to see your code in action.


## Developing

For this simple development walkthrough we'll add a new form "page" in the vuejs application.

1. First, create a Vuejs component in `/frontend/src/components/`. You can use a renamed copy of `form-example-2/FormExample2.vue` as a starting point.

2. Inside your Vuejs component file, `whatever.vue`, you'll have 3 blocks of interest:
  The `<template>` block contains all the HTML that your component uses. This will usually be some `<form>` and associated elements. 
  The `<script>` block contains the Vue instance definition for this particular component. You'll have to define some methods here to enable sending AJAX requests via the form in the template.
  The `<style>` block is where you put CSS styles that are specific to this component.
  The `<i18n>` block is where you put translation strings that are specific to this component.
  Add form input elements and some AJAX handling scripts to your component, save, and move on ...

3. In `/fontend/src/index.js`, add an `import` statement to the top of the file to import your component at build time. It should look a little something like this:
```
const WhatEverComponent = () => import('./components/what-ever/WhatEver.vue')
```

4. While still editing `/fontend/src/index.js`, scroll down to the `routes` variable declaration. Here you'll add a route for your component, so Vuejs can display your component at a given browser URL. Add a little route object like this:
```
const routes = [
  { path: '/', component: TableOfContents },
  ...,
  { path: '/whatever', component: WhatEverComponent } // Here is your route
]
```
Notice how you used the variale name from the `import` statement to define the `component` property.

5. Build! Go to `/frontend/` in a terminal and type `npm run build` to build the javascript. The final javascript is output to `/frontend/assets/js/aka.js`.

6. Enjoy! Open a browser and go to `localhost:8000/index#/whatever` to enjoy your work. You might want to do a hard refresh to clean the browser cache of any older version of the page.


## Technologies used

A quick rundown of the most interesting technologies in use in the frontend.

### Translations
The frontend is supposed to cater to both Danish and Greenlandic speakers. 
We have installed [vue-i18n](https://kazupon.github.io/vue-i18n/) and [vue-i18n-loader](https://github.com/kazupon/vue-i18n-loader) to do that.

In order to create translated text strings, add strings the `<i18>` block in your VUE component file. It will look a little like this:
```
<i18n>

    {
        "da": {
            "title": "Formular nummer 2",
            "inputa": "Inputfelt A",
            "inputb": "Inputfelt B",
            "send": "Send"
        },
        "kl": {
            "title": "Peqatigisanut ilitsersuutit",
            "inputa": "Imminut sullinnermi A",
            "inputb": "Maannakkut atorneqarnerpaasut B",
            "send": "Ilitsersuutit"
        }
    }

</i18n>
```
The JSON properties `da` and `kl` contain translated strings for Danish and Greenlandic respectively. Here the Danish string 'Inputfelt A' is referenced in templates by `$t('inputa')` and corresponds to the Greenlandic 'Imminut sullinnermi A'. (This is dummy text. I don't know any Greenlandic.)

Adding translated strings is a matter of adding the same property somewhere within BOTH the `da` and `kl` objects and then assigning them different texts.

#### Using translations
To use a translated string in a Vuejs component, open your `.vue` file and add `$t("someproperty")` wherever you need it in the `<template>` section of the code. Say, you wanted to add a translated 'Send' button using the message object from above, you would have to write:
```
<template>
    ...
    <button>{{ $t("send") }}</button>
    ...
</template>
```

If using translated strings within the `<script>` block, remember to refer to it using `this`.
```
<script>
    ...
    send_button_value = this.$t('send')
    ...
</script>
```


### AJAX

Sending a recieving AJAX requests in Vuejs is easy with [axios](https://github.com/axios/axios). We have implemented it, so you can do most AJAXing in your Vuejs components. 

Assume you have a `<form>` element in the template section that initiates a `sendForm()` method on submit
```
<form @submit.prevent="sendForm()">
  <input type="text" v-model="field_a">
  <input type="submit" value="Submit">
</form>
```
Then you can write a method in the script section to send the form data using axios like this:
```
sendForm: function() {

    let formdata = {
        input_a: this.field_a
    }

    axios({
        url: '/wherever-your-api-is',
        method: 'post',
        data: formdata,
        headers: {
            'X-CSRFToken': this.csrftoken,
            'X-AKA-BRUGER': 'Unknown'
        }
    })
    .then(res => {
        console.log('Success!')
    })
    .catch(err => {
        console.log('Something went wrong')
    })

}
```
Remember to supply the variables for `csrftoken` and `field_a`. There is a full example in `/frontend/src/components/form-example-2/FormExample2.vue`.


#### File upload

Check out `/frontend/src/components/form-example-2/FormExample2.vue` for an example implementation of a file upload using axios. It involves using [FormData](https://developer.mozilla.org/en-US/docs/Web/API/FormData) to wrap and send any binary file to the backend.


### Routing

Since the frontend is a single page web application, it needs internal routing to give the impression of moving from webpage to webpage, even though they are really just Vuejs components. We use [vue-router](https://router.vuejs.org/) for this.

WHen adding a new view, make sure to import it in `/frontend/src/index.js` and add a new route for it. (Check the details in the sections above.) If you need to link to other views using vue-router, check the examples in `/frontend/src/components/table_of_contents/TableOfContents.vue`.


### HTML <form> validation

Did you know that you can do basic input validation using native HTML5 attributes on input elements? You can set input fields to be required or conform to formats or regex. [Look it up at https://developer.mozilla.org/en-US/docs/Learn/HTML/Forms/Form_validation](https://developer.mozilla.org/en-US/docs/Learn/HTML/Forms/Form_validation).


### Notifications in the frontend

There is a little component that enables sending popup notifications in the UI. To use it, import it into the VUE component, where you need it like this:
```
<script>

    import { notify } from './components/utils/notify/Notifier.js'
    ...
```
Then use the `notify` method whenever you want to alert the user.
```
alertTheUser: function() {
    notify('You have been alerted.')
    notify(this.$t('This alert is translated'))
}
```
