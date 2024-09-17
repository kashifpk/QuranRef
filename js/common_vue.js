import { createApp } from 'vue'
import { createPinia } from 'pinia'
import vuetify from './plugins/vuetify'
import router from './router'

function mountVueComponent(elementId, Component) {
  const elem = document.getElementById(elementId)
  const pinia = createPinia()

  const app = createApp(Component)
  // Register a global custom directive called `v-focus`
  // app.directive('focus', {
  //   // When the bound element is mounted into the DOM...
  //   mounted(el) {
  //   // Focus the element
  //   el.focus()
  //   }
  // })

  app.use(vuetify)
  app.use(router)
  app.use(pinia)
  app.mount(elem)
}

export default mountVueComponent;
