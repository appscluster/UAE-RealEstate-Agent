import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 43231,
    proxy: {
      '/api': 'http://127.0.0.1:54231',
      '/runs': 'http://127.0.0.1:54231',
    },
  },
  preview: { port: 43231 },
})
