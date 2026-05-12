import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // указываем: все запросы, начинающиеся с /api, нужно перехватывать
      '/api': {
        target: 'https://mock-y.ru/', // твой удаленный сервер
        changeOrigin: true, // меняем заголовок host, чтобы бэк думал, что запрос пришел от него же
        secure: true, // оставляем true, так как у тебя настроен https
      }
    }
  }
})