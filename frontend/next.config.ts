import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["*"],
  // Prevent Next.js from stripping trailing slashes before rewrites run.
  // Without this, /backend/generate-schedules/ → /backend/generate-schedules
  // and FastAPI returns 307 (or 404) because it expects the slash.
  skipTrailingSlashRedirect: true,

  // Proxy /backend/* → backend container (Docker internal network).
  // The browser never talks to the backend directly — no CORS needed.
  // BACKEND_INTERNAL_URL is server-side only (not NEXT_PUBLIC_*).
  async rewrites() {
    const backendUrl =
      process.env.BACKEND_INTERNAL_URL || "http://localhost:8000";
    return [
      {
        source: "/backend/:path*",
        destination: `${backendUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
