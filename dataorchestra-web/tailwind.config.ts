import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#08111f",
        graphite: "#111827",
        panel: "#101a2b",
        line: "#263244",
        cyan: "#40d9f1",
        mint: "#67e8a5",
        amber: "#f2c96d"
      },
      boxShadow: {
        soft: "0 20px 80px rgba(0, 0, 0, 0.28)"
      }
    }
  },
  plugins: []
};

export default config;
