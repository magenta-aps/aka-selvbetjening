import Vue from 'vue'
import VueRouter from 'vue-router'
import VueI18n from 'vue-i18n'
import { messages } from './i18n/Messages.js'
import App from './App.vue'
import TableOfContents from './components/table_of_contents/TableOfContents.vue'
import FormExample1 from './components/form_example_1/FormExample1.vue'
import FormExample2 from './components/form_example_2/FormExample2.vue'

//
// Vue.use(VueI18n)

Vue.use(VueRouter)
Vue.use(VueI18n)

const routes = [
  { path: '/', component: TableOfContents },
  { path: '/form1', component: FormExample1 },
  { path: '/form2', component: FormExample2 }
]

const router = new VueRouter({
  routes: routes
})

const i18n = new VueI18n({
  locale: 'kl', // set locale
  fallbackLocale: 'da',
  messages: messages, // set locale messages
})

const app = new Vue({
  el: '#aka-app',
  router: router,
  i18n: i18n,
  render: h => h(App)
})
