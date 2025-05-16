import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import typescript from '@rollup/plugin-typescript';
import tailwindcss from 'tailwindcss';
import { vite } from './src/config/config';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), typescript(), tailwindcss('./tailwind.config.js')],
  server: vite.server,
});
