/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        gabon: {
          green: '#009e60',
          50: '#e6f5eb',
          100: '#c2e6cd',
          200: '#9ad4ad',
          300: '#6fc28d',
          400: '#45b06d',
          500: '#009e60',
          600: '#008050',
          700: '#006340',
          800: '#004530',
          900: '#002820',
        },
      },
      fontFamily: {
        mono: ['Geist Mono', 'monospace'],
        sans: ['Inter Display', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}