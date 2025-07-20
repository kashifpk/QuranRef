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
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#4CAF50',     // Green
          secondary: '#81C784',   // Light Green  
          accent: '#66BB6A',      // Medium Green
          success: '#4CAF50',     // Green
          info: '#2196F3',        // Blue
          warning: '#FF9800',     // Orange
          error: '#F44336',       // Red
          background: '#FAFAFA',  // Very Light Gray
          surface: '#FFFFFF',     // White
        }
      }
    }
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
