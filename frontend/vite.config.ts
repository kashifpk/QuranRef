import path from 'path'
import { resolve } from 'path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { config } from 'dotenv'

config({ path: path.join(__dirname, '.env') })

const STATIC_URL = process.env.STATIC_URL || '/static/'

// https://vitejs.dev/config/
export default defineConfig({
  base: process.env.NODE_ENV === 'production' ? `${STATIC_URL}` : '/',
  css: {
    devSourcemap: true,
  },
  plugins: [vue()],
  build: {
    target: 'esnext',
    outDir: resolve('../static/frontend/'),
    emptyOutDir: true,
    assetsDir: '',
    manifest: 'manifest.json',
    rollupOptions: {
      input: resolve('./index.html')
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': 'http://backend:8000'
    }
  },
  // Configure for SPA routing
  preview: {
    port: 5173,
    host: '0.0.0.0'
  }
})
