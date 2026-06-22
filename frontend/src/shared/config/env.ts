const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();

export const env = {
  apiBaseUrl: (rawApiBaseUrl || "/api/v1").replace(/\/$/, ""),
  reviewerId: import.meta.env.VITE_REVIEWER_ID?.trim() || "frontend-reviewer",
} as const;
