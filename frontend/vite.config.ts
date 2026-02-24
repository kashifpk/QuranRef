import path from 'path'
import { resolve } from 'path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { config } from 'dotenv'

config({ path: path.join(__dirname, '.env') })

const STATIC_URL = process.env.STATIC_URL || '/static/'
// Use VITE_BACKEND_URL for proxy target, defaulting to localhost for host development
const BACKEND_URL = process.env.VITE_BACKEND_URL || 'http://localhost:41148'

// https://vitejs.dev/config/
export default defineConfig({
  base: process.env.NODE_ENV === 'production' ? `${STATIC_URL}` : '/',
  css: {
    devSourcemap: true,
  },
  plugins: [vue()],
  build: {
    target: 'esnext',
    outDir: resolve('../static/'),
    emptyOutDir: true,
    assetsDir: '',
    manifest: 'manifest.json',
    rollupOptions: {
      input: resolve('./index.html')
    },
  },
  server: {
    host: '0.0.0.0',
    port: 41149,
    proxy: {
      '/api': BACKEND_URL
    },
    watch: {
      // Polling required for containerized development
      // Native inotify events reach container but chokidar doesn't receive them
      usePolling: true,
      interval: 500
    }
  },
  // Configure for SPA routing
  preview: {
    port: 41149,
    host: '0.0.0.0'
  }
})
