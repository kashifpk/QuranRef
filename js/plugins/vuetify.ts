import 'vuetify/styles'

import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

const vuetify = createVuetify({
  defaults: {
    global: {
      transition: false,
      ripple: false,
    },
  },
  theme: {
    defaultTheme: 'light'
  },

  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    }
  }
})

export default vuetify
