import { env } from "@/shared/config/env";
import type { ApiErrorEnvelope } from "@/shared/types/api";

interface ApiRequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  token?: string;
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly details?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");

  if (options.body !== undefined) headers.set("Content-Type", "application/json");
  if (options.token) headers.set("Authorization", `Bearer ${options.token}`);

  let response: Response;
  try {
    response = await fetch(`${env.apiBaseUrl}${path}`, {
      ...options,
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ApiError(
      0,
      "NETWORK_ERROR",
      `Cannot connect to API at ${env.apiBaseUrl}.`,
      error instanceof Error ? error.message : undefined,
    );
  }

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as ApiErrorEnvelope | null;
    throw new ApiError(
      response.status,
      payload?.error.code ?? "HTTP_ERROR",
      payload?.error.message ?? `Request failed with status ${response.status}`,
      payload?.error.details,
    );
  }

  return response.json() as Promise<T>;
}
