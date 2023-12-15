import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import typescript from '@rollup/plugin-typescript';
import tailwindcss from 'tailwindcss';

function getTarget() {
  //npm run prod  -> 'https://softball.jameskabbes.com/api'
  //npm run dev  ->  'http://127.0.0.1:8086'

  if (process.env.JAMESKABBES_PROD == 'true') {
    return 'https://softball.jameskabbes.com/api';
  } else {
    return 'http://127.0.0.1:8086';
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), typescript(), tailwindcss('./tailwind.config.js')],
  server: {
    host: true,
    port: 3000,
    proxy: {
      '/api': {
        target: getTarget(),
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});
