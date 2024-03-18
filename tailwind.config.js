/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["**/*.html"],
    darkMode: ["selector", ".dark"],
    theme: {
        extend: {},
        fontFamily: {
            sans: ["'Readex Pro', sans-serif"],
        },
    },
    plugins: [require("daisyui"), require("@tailwindcss/typography")],
};
