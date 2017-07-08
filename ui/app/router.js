import Vue from 'vue'
import VueRouter from 'vue-router'

import store from './store'

import App from './App.vue'
import Login from './Login.vue'

import Dashboard from './containers/Dashboard.vue'
import Keys from './containers/Keys.vue'

Vue.use(VueRouter)

const routes = [
  { path: '/login', component: Login },
  { path: '/', component: App,
    children: [
      { path: '/dashboard', component: Dashboard, meta: { title: 'Dashboard' } },
      { path: '/keys', component: Keys, meta: { title: 'Keys' } },
      { path: '/', redirect: '/dashboard' }
    ]
  }
]

function auth (to, from, next) {
  if (!store.state.auth.isLoggedIn) {
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else {
    next()
  }
}

async function logout (to, from, next) {
  await store.dispatch('logout')
  next('/login')
}

const router = new VueRouter({
  mode: 'history',
  routes
})

export default router
