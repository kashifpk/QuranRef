import 'vite/modulepreload-polyfill'

import mountVueComponents from './common_vue.ts'
import QuranRefMainApp from './QuranRefMainApp.vue'

const availableComponents = [QuranRefMainApp]
const componentMap = availableComponents.reduce((acc: { [key: string]: any }, component) => {
  const componentNameInKebabCase = component.__name ? component.__name.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').slice(1).toLowerCase() : ''
  acc[componentNameInKebabCase] = component
  return acc
},
  {}
)

mountVueComponents(componentMap)
