import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import typescript from '@rollup/plugin-typescript';
import tailwindcss from 'tailwindcss';
import siteConfig from './siteConfig.json';

function getTarget() {
  if (process.env.JAMESKABBES_PROD == 'true') {
    return `https://${siteConfig.domain_name}/${siteConfig.api_endpoint_base}`;
  } else {
    return 'http://127.0.0.1:8087';
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), typescript(), tailwindcss('./tailwind.config.js')],
  server: {
    host: true,
    port: 3000,
    proxy: {
      [`/${siteConfig.api_endpoint_base}`]: {
        target: getTarget(),
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});
