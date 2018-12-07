import Vue from 'vue'
import App from './App.vue'
import router from './router'
import VueI18n from 'vue-i18n'
import VeeValidate from 'vee-validate'
import validationMessagesEn from 'vee-validate/dist/locale/en'
import validationMessagesDa from 'vee-validate/dist/locale/da'
import { messages } from './i18n/Messages'
import SimpleField from '@/components/simple_field/SimpleField'
import '@/assets/css/base-styles.css'

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
  dictionary: {
    kl: validationMessagesEn,
    da: validationMessagesDa
  }
})

new Vue({
  router,
  i18n,
  render: h => h(App)
}).$mount('#aka-app')
