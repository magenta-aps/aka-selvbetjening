import Vue from 'vue'
import VueRouter from 'vue-router'
import App from './App.vue'
import TableOfContents from './components/table_of_contents/TableOfContents.vue'
import FormExample1 from './components/form_example_1/FormExample1.vue'
import FormExample2 from './components/form_example_2/FormExample2.vue'

Vue.use(VueRouter)

const routes = [
  { path: '/', component: TableOfContents },
  { path: '/form1', component: FormExample1 },
  { path: '/form2', component: FormExample2 }
]

const router = new VueRouter({
  routes: routes
})

const app = new Vue({
  el: '#aka-app',
  router: router,
  render: h => h(App)
})
