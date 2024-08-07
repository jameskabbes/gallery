import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import typescript from '@rollup/plugin-typescript';
import tailwindcss from 'tailwindcss';

import config from '../config.json';

function getApiTarget() {
  if (process.env.VITE_APP_MODE == 'development') {
    return 'http://127.0.0.1:8087';
  } else {
    return `https://${config.domain_name}/${config.api_endpoint_base}`;
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), typescript(), tailwindcss('./tailwind.config.js')],
  server: {
    host: true,
    port: 3000,
    proxy: {
      [`/${config.api_endpoint_base}`]: {
        target: getApiTarget(),
        changeOrigin: true,
        rewrite: (path) =>
          path.replace(new RegExp(`^/${config.api_endpoint_base}`), ''),
      },
    },
  },
});

export { getApiTarget };
