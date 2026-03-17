import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 环境变量配置
// VITE_API_URL: 生产环境 API 地址（不包含 /api 前缀）
// 示例: https://api.yourdomain.com

export default defineConfig(({ mode }) => {
  const isProduction = mode === 'production'
  // 生产环境使用相对路径，通过 nginx 代理到后端
  const apiUrl = isProduction ? '' : (process.env.VITE_API_URL || '')

  return {
    plugins: [vue()],
    base: '/',

    // 开发服务器配置
    server: {
      port: 3000,
      proxy: isProduction ? {} : {
        '/api': {
          target: 'http://localhost:8080',
          changeOrigin: true
        }
      }
    },

    // 生产构建配置
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: false,
      minify: 'esbuild'
    },

    // 环境变量前缀
    envPrefix: 'VITE_'
  }
})
