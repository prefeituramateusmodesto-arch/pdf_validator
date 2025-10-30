import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Configuração de build para Vercel (React + Vite)
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist', // saída padrão
  },
  server: {
    port: 5173,
    open: true,
  },
});
