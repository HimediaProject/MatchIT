import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  envDir: '../',
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
<<<<<<< HEAD
  },
=======
    historyApiFallback: true,
  }
>>>>>>> ae4afd53f00d5287960daae91e036fff2c697340
})
