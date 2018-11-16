import Vue from 'vue'
import App from './App.vue'
import router from './router'
import VueI18n from 'vue-i18n'
import { messages } from './i18n/Messages'
import SimpleField from '@/components/simple_field/SimpleField'
import '@/assets/css/base-styles.css'

Vue.use(VueI18n)
Vue.component('s-field', SimpleField)

const i18n = new VueI18n({
  locale: 'kl', // set locale
  fallbackLocale: 'da',
  messages
})

new Vue({
  router,
  i18n,
  render: h => h(App)
}).$mount('#aka-app')
