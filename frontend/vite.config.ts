import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import typescript from '@rollup/plugin-typescript';
import tailwindcss from 'tailwindcss';
import { importedConfig } from './importConfig';

// https://vitejs.dev/config/
export default defineConfig({
  define: {
    'import.meta.env.VITE_APP_CONFIG': JSON.stringify(importedConfig),
  },

  plugins: [react(), typescript()],
  server: importedConfig.vite.server,
});
