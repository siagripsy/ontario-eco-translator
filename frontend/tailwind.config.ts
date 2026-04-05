import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#f6f8f6",
        ink: "#16342f",
        mist: "#edf4f0",
        emerald: "#1f6b5b",
        teal: "#0d766e",
        amber: "#d29b2d",
        slate: "#62727b",
      },
      boxShadow: {
        panel: "0 20px 60px rgba(21, 55, 47, 0.10)",
        soft: "0 10px 30px rgba(16, 48, 40, 0.08)",
      },
      borderRadius: {
        "4xl": "2rem",
      },
      backgroundImage: {
        "hero-radial":
          "radial-gradient(circle at top left, rgba(22, 118, 110, 0.12), transparent 36%), radial-gradient(circle at top right, rgba(210, 155, 45, 0.12), transparent 24%)",
      },
    },
  },
  plugins: [],
} satisfies Config;
