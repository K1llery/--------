import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [tailwindcss(), vue()],
  server: {
    port: 5173,
    proxy: {
      // Backend-served media (uploaded files, AI-generated images)
      "/media/uploads": "http://127.0.0.1:8000",
      "/media/generated": "http://127.0.0.1:8000",
    },
  },
});
