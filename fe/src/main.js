import Vue from 'vue'
import App from './App.vue'
import store from './store'
import VueYoutube from 'vue-youtube'

Vue.use(VueYoutube)
Vue.config.productionTip = false

new Vue({
  store,
  render: h => h(App)
}).$mount('#app')
