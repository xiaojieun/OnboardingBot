import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 配置Vite开发服务器并代理后端接口
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
