import { Component, createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Tooltip from 'primevue/tooltip'
import { primeVueConfig } from './plugins/primevue.ts'
import router from './router.ts'


function mountVueComponents(componentMap: Record<string, Component>) {
  const pinia = createPinia()

  const vcElements = document.getElementsByClassName('vc');
  if (vcElements.length > 0) {
    for (let i = 0; i < vcElements.length; i++) {
      const element = vcElements[i] as HTMLElement;
      const firstVClass = Array.from(element.classList).find(cls => cls.startsWith('v-'));
      if (!firstVClass) {
        console.error('No v- class found in vc element', element);
        continue;
      }

      const elementClass = firstVClass.slice(2);
      const Component = componentMap[elementClass];
      if (Component) {
        const app = createApp(Component, element.dataset);
        app.use(PrimeVue, primeVueConfig)
        app.directive('tooltip', Tooltip)
        app.use(router)
        app.use(pinia)
        app.mount(element);
      }
    }
    return;
  }

}

export default mountVueComponents;
