import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    proxy: {
      '/assets': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  test: {
    include: ['src/tests/**/*.test.ts'],
    environment: 'jsdom',
    globals: true,
    setupFiles: ['src/tests/setup.ts']
  }
});
