import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Assets load relative to the page, so the app runs under any base path.
export default defineConfig({
  base: "./",
  plugins: [react()],
  server: { proxy: { "/api": "http://localhost:8000" } },
});
