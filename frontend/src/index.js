import Vue from 'vue'
import VueRouter from 'vue-router'
import VueI18n from 'vue-i18n'
import App from './App.vue'
import VeeValidate from 'vee-validate'

const TableOfContents = () => import('./components/table_of_contents/TableOfContents.vue')
const DesignGuide = () => import('./components/designguide/DesignGuide.vue')

const FormExample1 = () => import('./components/form_example_1/FormExample1.vue')
const FormExample2 = () => import('./components/form_example_2/FormExample2.vue')
const IndberetFordring = () => import ('./components/indberet_fordring/IndberetFordring.vue')
const Experiment = () => import('./components/experiment_with_file_upload/Example.vue')

Vue.use(VueRouter)
Vue.use(VueI18n)
Vue.use(VeeValidate)

const routes = [
  { path: '/', component: TableOfContents },
  { path: '/designguide', component: DesignGuide },
  
  { path: '/form1', component: FormExample1 },
  { path: '/form2', component: FormExample2 },
  { path: '/indberetning', component: IndberetFordring},
  { path: '/upload', component: Experiment }
]

const router = new VueRouter({
  routes: routes
})

const i18n = new VueI18n({
  locale: 'kl', // set locale
  fallbackLocale: 'da'
})

const app = new Vue({
  el: '#aka-app',
  router: router,
  i18n: i18n,
  render: h => h(App)
})
