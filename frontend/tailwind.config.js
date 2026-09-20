/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#FAFAF8",
        surface: "#FFFFFF",
        ink: "#1A1D1B",
        "ink-muted": "#5B6058",
        hairline: "#DEDCD3",
       
        mark: "#2B4C3F",
        
        status: {
          corroborated: "#1F6F4A",
          "corroborated-bg": "#EAF3EE",
          contested: "#9A5B12",
          "contested-bg": "#FBF1E4",
          conflicting: "#A13A2E",
          "conflicting-bg": "#FBEBE8",
          unresolved: "#6B6558",
          "unresolved-bg": "#F1EFEA",
          none: "#8A8578",
          "none-bg": "#F1EFEA",
        },
      },
      fontFamily: {
        sans: [
          "IBM Plex Sans", "ui-sans-serif", "system-ui", "-apple-system", "sans-serif",
        ],
        mono: [
          "IBM Plex Mono", "ui-monospace", "SFMono-Regular", "Menlo", "monospace",
        ],
      },
    },
  },
  plugins: [],
};
