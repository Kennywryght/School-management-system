import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'https://school-management-system-2-wck6.onrender.com',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist'
  }
})