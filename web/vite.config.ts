import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Dev: the Vite server proxies /api to the FastAPI backend so the SPA is
// same-origin in development too. Prod: `vite build` output is served BY
// FastAPI (ADR 0022) — fully offline, no Node runtime.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/api": { target: "http://localhost:8000", changeOrigin: false },
    },
  },
});
