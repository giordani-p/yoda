/// <reference types="vitest/config" />
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@": "/src" } },
  // Lê o .env da raiz do repositório (variáveis VITE_*).
  envDir: "../../",
  server: { port: 5173 },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test-setup.ts"],
  },
});
