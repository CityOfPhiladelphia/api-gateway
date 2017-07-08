import Vue from 'vue'
import Vuetify from 'vuetify'
import VueMoment from 'vue-moment'

import router from './router'

Vue.use(Vuetify)
Vue.use(VueMoment)

new Vue({
  el: '#app',
  router
})
