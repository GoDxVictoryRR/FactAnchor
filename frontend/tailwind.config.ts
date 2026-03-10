import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./src/app/**/*.{ts,tsx}",
        "./src/components/**/*.{ts,tsx}",
        "./src/lib/**/*.{ts,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ["var(--font-sans)", "system-ui", "sans-serif"],
                mono: ["var(--font-mono)", "monospace"],
            },
            animation: {
                "count-up": "countUp 600ms ease-out forwards",
                "fade-in": "fadeIn 150ms ease-out forwards",
                "scale-in": "scaleIn 300ms ease-out forwards",
            },
            keyframes: {
                countUp: {
                    "0%": { opacity: "0", transform: "scale(0.8)" },
                    "100%": { opacity: "1", transform: "scale(1)" },
                },
                fadeIn: {
                    "0%": { opacity: "0", transform: "translateY(4px)" },
                    "100%": { opacity: "1", transform: "translateY(0)" },
                },
                scaleIn: {
                    "0%": { opacity: "0", transform: "scale(0.8)" },
                    "100%": { opacity: "1", transform: "scale(1)" },
                },
            },
        },
    },
    plugins: [],
};

export default config;
