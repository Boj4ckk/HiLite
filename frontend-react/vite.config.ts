import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // ← Écoute sur toutes les interfaces
    port: 5173,
    watch: {
      usePolling: true  // ← Important pour hot-reload dans Docker
    }
  }
})
