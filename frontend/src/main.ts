import 'primeicons/primeicons.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Tooltip from 'primevue/tooltip'
import { primeVueConfig } from './plugins/primevue.ts'
import router from './router.ts'
import QuranRefMainApp from './QuranRefMainApp.vue'

const app = createApp(QuranRefMainApp)
app.use(PrimeVue, primeVueConfig)
app.directive('tooltip', Tooltip)
app.use(router)
app.use(createPinia())
app.mount('#app')
