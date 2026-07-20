import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f0f9f6",
          100: "#d9f0e8",
          500: "#0f9d6c",
          600: "#0c7f58",
          700: "#0a6647",
        },
      },
    },
  },
  plugins: [],
};

export default config;
