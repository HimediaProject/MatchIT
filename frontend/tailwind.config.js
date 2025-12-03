/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef6ff',
          100: '#d9eaff',
          200: '#b7d5ff',
          300: '#8cb7ff',
          400: '#5a91ff',
          500: '#2d6dff',
          600: '#1c51d6',
          700: '#1740aa',
          800: '#153885',
          900: '#132f6b',
        },
        accent: '#f59f00',
        slate: {
          950: '#0b1021',
        },
      },
      fontFamily: {
        sans: ['"Noto Sans KR"', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 16px 48px -20px rgba(16, 24, 40, 0.35)',
      },
    },
  },
  plugins: [],
}
