import path from "node:path";
import { fileURLToPath } from "node:url";

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

const currentDirectory = path.dirname(fileURLToPath(import.meta.url));
const defaultProxyTarget = "http://127.0.0.1:8000";

export default defineConfig(({ mode }) => {
  const apiBaseUrl = loadEnv(mode, currentDirectory, "VITE_").VITE_API_BASE_URL?.trim();
  let proxyTarget = defaultProxyTarget;

  if (apiBaseUrl) {
    try {
      proxyTarget = new URL(apiBaseUrl).origin;
    } catch {
      proxyTarget = defaultProxyTarget;
    }
  }

  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        "@": path.resolve(currentDirectory, "./src"),
      },
    },
    server: {
      port: 5173,
      proxy: {
        "/api": {
          target: proxyTarget,
          changeOrigin: true,
        },
      },
    },
  };
});
