import 'vite/modulepreload-polyfill'
import 'primeicons/primeicons.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Tooltip from 'primevue/tooltip'
import { primeVueConfig } from './plugins/primevue.ts'
import router from './router.ts'
import QuranRefMainApp from './QuranRefMainApp.vue'
import mountVueComponents from './common_vue.ts'

// Check if we're in development mode with a standalone app mount point
const appElement = document.getElementById('app')
if (appElement) {
  // Development mode - mount the full app
  const app = createApp(QuranRefMainApp)
  const pinia = createPinia()

  app.use(PrimeVue, primeVueConfig)
  app.directive('tooltip', Tooltip)
  app.use(router)
  app.use(pinia)
  app.mount('#app')
} else {
  // Production mode - use the component mounting system
  const availableComponents = [QuranRefMainApp]
  const componentMap = availableComponents.reduce((acc: { [key: string]: any }, component) => {
    const componentNameInKebabCase = component.__name ? component.__name.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').slice(1).toLowerCase() : ''
    acc[componentNameInKebabCase] = component
    return acc
  }, {})

  mountVueComponents(componentMap)
}
