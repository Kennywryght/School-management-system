import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  build: {
    outDir: 'dist',
    sourcemap: true
  },
  server: {
    host: '0.0.0.0',
    port: 10000
  }
})