import { resolve } from 'path'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Loads .env, .env.local, .env.[mode] from this directory. Existing process
  // environment variables take priority, so containers can override these.
  const env = loadEnv(mode, import.meta.dirname, '')
  const STATIC_URL = env.STATIC_URL || '/static/'
  // Proxy target for /api during development. Defaults to the host backend.
  const BACKEND_URL = env.VITE_BACKEND_URL || 'http://localhost:41148'

  return {
    base: mode === 'production' ? STATIC_URL : '/',
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
        input: resolve('./index.html'),
      },
    },
    server: {
      host: '0.0.0.0',
      port: 41149,
      proxy: {
        '/api': BACKEND_URL,
      },
      watch: {
        // Polling is required for containerized development: native inotify
        // events reach the container but chokidar does not receive them.
        usePolling: true,
        interval: 500,
      },
    },
    preview: {
      port: 41149,
      host: '0.0.0.0',
    },
  }
})
