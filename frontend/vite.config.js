import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './', // necessário para evitar erro 404 ao recarregar a página
  build: {
    outDir: 'dist', // pasta padrão que o Render usará para publicar
  },
  server: {
    port: 5173,
    host: true,
  },
})
