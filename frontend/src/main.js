import Vue from 'vue'
import App from './App.vue'
import router from './router'
import VueI18n from 'vue-i18n'
import VeeValidate, { Validator } from 'vee-validate'
import attributesDa from './i18n/attributes/da'
import messagesKl from './i18n/messages/kl'
import messagesDa from './i18n/messages/da'
import attributesKl from './i18n/attributes/kl'
import validationMessagesEn from 'vee-validate/dist/locale/en'
import validationMessagesDa from 'vee-validate/dist/locale/da'
import { messages } from './i18n/Messages'
import SimpleField from '@/components/simple_field/SimpleField'
import '@/assets/css/base-styles.css'
import installRules from './custom_rules'

Vue.use(VueI18n)

Vue.component('s-field', SimpleField)

if (localStorage.getItem('language') == null) {
  localStorage.setItem('language', 'kl')
}

const i18n = new VueI18n({
  locale: localStorage.getItem('language'), // set locale
  fallbackLocale: 'da',
  messages
})

Vue.use(VeeValidate, {
  i18nRootKey: 'validations', // customize the root path for validation messages.
  i18n,
  validity: true,
  dictionary: {
    kl: validationMessagesEn, // defaults to English. Greenlandic is not supported -- would need pull request to the vee validate team
    da: validationMessagesDa
  }
})

installRules(Validator)

const dict = {
  kl: {
    messages: messagesKl,
    attributes: attributesKl
  },
  da: {
    messages: messagesDa,
    attributes: attributesDa
  }
}
Validator.localize(dict)

new Vue({
  router,
  i18n,
  render: h => h(App)
}).$mount('#aka-app')
