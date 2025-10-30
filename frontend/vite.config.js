import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Configuração padrão do Vite para React
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist', // pasta de saída do build
  },
  server: {
    port: 5173,
    open: true,
  },
});
