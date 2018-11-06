import Vue from 'vue'
import Router from 'vue-router'

const TableOfContents = () => import('@/components/table_of_contents/TableOfContents.vue')
const DesignGuide = () => import('@/components/designguide/DesignGuide.vue')

const FormExample1 = () => import('@/components/form_example_1/FormExample1.vue')
const FormExample2 = () => import('@/components/form_example_2/FormExample2.vue')
const IndberetFordring = () => import('@/components/indberet_fordring/IndberetFordring.vue')
const Experiment = () => import('@/components/experiment_with_file_upload/Example.vue')
const GetRentenota = () => import('@/components/rentenota/GetRentenota.vue')

Vue.use(Router)

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      component: TableOfContents
    },
    {
      path: '/designguide',
      name: 'DesignGuide',
      component: DesignGuide
    },
    {
      path: '/rentenota',
      component: GetRentenota
    },
    {
      path: '/form1',
      component: FormExample1
    },
    {
      path: '/form2',
      component: FormExample2
    },
    {
      path: '/indberetning',
      component: IndberetFordring
    },
    {
      path: '/upload',
      component: Experiment
    }
  ]
})
