import 'vite/modulepreload-polyfill'

import mountVueComponent from './common_vue'
import App from './App.vue'

mountVueComponent('qref-main', App)
