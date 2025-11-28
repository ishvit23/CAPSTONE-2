// Use relative path in production (nginx will proxy to backend)
// Use environment variable for local development
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "/api";

