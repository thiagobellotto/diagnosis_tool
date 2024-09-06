/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{html,js}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        alabaster: "#FAFAFA",
        snow: "#F8F9FA",
        seashell: "#F1F1F1",
        ghostWhite: "#F8F8FF",
      },
    },
  },
  plugins: [],
};
