/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        'midnight-void': '#12131C',
        'charcoal-surface': '#1A1C26',
        'royal-blue': '#2563EB',
        'emerald-glow': '#10B981',
        'muted-label': '#94A3B8'
      }
    },
  },
  plugins: [],
}

