import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import typescript from '@rollup/plugin-typescript';
import tailwindcss from 'tailwindcss';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), typescript(), tailwindcss('./tailwind.config.js')],
  server: {
    host: true,
    port: 3000,
  },
});
