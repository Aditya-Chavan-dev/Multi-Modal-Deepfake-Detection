/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            animation: {
                'scan': 'scan 2s linear infinite',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                scan: {
                    '0%': { transform: 'translateY(-100%)' },
                    '100%': { transform: 'translateY(100%)' },
                }
            },
            colors: {
                background: '#09090b', // zinc-950
                surface: '#18181b', // zinc-900
                border: '#27272a', // zinc-800
                primary: '#fafafa', // zinc-50
                secondary: '#a1a1aa', // zinc-400
            }
        },
    },
    plugins: [],
}
