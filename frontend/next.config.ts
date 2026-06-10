import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["*"],

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
