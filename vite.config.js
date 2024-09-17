import path from 'path'
import { resolve } from 'path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { config } from 'dotenv'

config({ path: path.join(__dirname, '.env') })

const STATIC_URL = process.env.STATIC_URL || '/static/'

// https://vitejs.dev/config/
export default defineConfig({
  base: `${STATIC_URL}`,
  css: {
    devSourcemap: true,
  },
  plugins: [vue()],
  build: {
    target: 'esnext',
    outDir: resolve('./static/'),
    emptyOutDir: false,
    assetsDir: '',
    manifest: 'manifest.json',
    rollupOptions: {
      input: {
        main: resolve('./js/main.js')
      },
    },
    root: "."
  },
  server: {
    port: 5173
  },
  test: {
    environment: 'jsdom',
    include: ['js_tests/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}']
  }
})
