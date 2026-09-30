/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "primary": "#ffc174",
        "primary-container": "#f59e0b",
        "on-primary": "#472a00",
        "on-primary-container": "#613b00",
        "background": "#0f141b",
        "surface": "#0f141b",
        "surface-container-lowest": "#090f15",
        "surface-container-low": "#171c23",
        "surface-container": "#1b2027",
        "surface-container-high": "#252a32",
        "surface-container-highest": "#30353d",
        "outline": "#a08e7a",
        "outline-variant": "#534434",
        "on-surface": "#dee2ec",
        "on-surface-variant": "#d8c3ad",
        "tertiary": "#6de575",
        "tertiary-container": "#4fc85d",
        "error": "#ffb4ab",
        "error-container": "#93000a",
        "secondary": "#a2c9ff"
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"]
      }
    },
  },
  plugins: [],
}
