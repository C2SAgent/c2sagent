import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    host: '0.0.0.0',  // 允许外部访问
    port: 5173,
    allowedHosts: [
      'www.c2sagent.com',  // 允许的主机名
      'c2sagent.com'      // 如果需要，也允许无 www 的域名
    ]
  }
})