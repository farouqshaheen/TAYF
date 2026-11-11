import { defineConfig } from 'vite';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const projectRoot = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  base: './',
  publicDir: false,
  build: {
    outDir: resolve(projectRoot, '../../static/doctor_character'),
    emptyOutDir: false,
    assetsDir: 'assets',
    chunkSizeWarningLimit: 700,
    rollupOptions: {
      output: {
        entryFileNames: 'assets/doctor-viewer.js',
        chunkFileNames: 'assets/doctor-chunk-[name].js',
        assetFileNames: 'assets/doctor-style.[ext]',
      },
    },
  },
});
