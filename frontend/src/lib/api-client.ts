const getApiUrl = (endpoint: string): string => {
  // Empty string → use the /backend proxy (same-origin, no CORS).
  // Set NEXT_PUBLIC_API_URL to an external URL only when the backend
  // is exposed directly (e.g. local dev without Docker).
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "/backend"
  return `${baseUrl}${endpoint}`
}

export { getApiUrl }
