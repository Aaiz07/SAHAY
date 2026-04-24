/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        glass: 'rgba(255,255,255,0.07)',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
};
