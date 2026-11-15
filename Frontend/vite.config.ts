import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: "0.0.0.0", // Exposes to your local network (or use true, or a custom IP/host)
    port: 3000, // Changes the default 5173 port to 3000
    strictPort: true, // Optional: fails instead of auto-incrementing if port is busy
  },
  resolve: {
    alias: {
      // Maps '@' to the 'src' directory
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
