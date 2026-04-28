/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#05070A',
          surface: '#0F172A',
          card: 'rgba(15, 23, 42, 0.8)',
        },
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
        accent: {
          cyan: '#22D3EE',
          indigo: '#818CF8',
        }
      },
      fontFamily: {
        lexend: ['Lexend', 'sans-serif'],
        geist: ['Geist', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'glow-brand': '0 0 20px rgba(56, 189, 248, 0.15)',
        'glow-accent': '0 0 25px rgba(34, 211, 238, 0.2)',
      }
    },
  },
  plugins: [],
}
