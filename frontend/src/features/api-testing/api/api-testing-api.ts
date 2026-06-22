import type { ApiErrorEnvelope } from "@/shared/types/api";
import { env } from "@/shared/config/env";
import type { ApiTestRequest, ApiTestResponse } from "@/features/api-testing/types";

function resolveApiUrl(path: string) {
  const apiPrefix = "/api/v1";
  if (path.startsWith(apiPrefix) && env.apiBaseUrl.endsWith(apiPrefix)) {
    return `${env.apiBaseUrl}${path.slice(apiPrefix.length)}`;
  }
  return `${env.apiBaseUrl}${path.startsWith("/") ? path : `/${path}`}`;
}

function networkError(error: unknown, latencyMs: number): ApiTestResponse {
  const body: ApiErrorEnvelope = {
    error: {
      code: "NETWORK_ERROR",
      message: `Cannot connect to API at ${env.apiBaseUrl}.`,
      details: error instanceof Error ? error.message : null,
    },
  };
  const raw = JSON.stringify(body, null, 2);
  return {
    status: 0,
    statusText: "Network Error",
    latencyMs,
    size: `${new Blob([raw]).size} B`,
    headers: {},
    body,
    raw,
  };
}

export async function sendApiTestRequest(request: ApiTestRequest): Promise<ApiTestResponse> {
  const startedAt = performance.now();
  const headers = new Headers({ Accept: "application/json" });
  if (request.endpoint.auth && request.token.trim()) {
    headers.set("Authorization", `Bearer ${request.token.trim()}`);
  }

  const hasBody = request.endpoint.method === "POST" || request.endpoint.method === "PATCH";
  if (hasBody && request.body.trim()) headers.set("Content-Type", "application/json");

  let path = request.endpoint.path.replace("{id}", encodeURIComponent(request.pathParam.trim()));
  const query = new URLSearchParams(
    Object.entries(request.query).filter(([, value]) => value.trim() !== ""),
  ).toString();
  if (query) path += `?${query}`;

  try {
    const response = await fetch(resolveApiUrl(path), {
      method: request.endpoint.method,
      headers,
      body: hasBody && request.body.trim() ? request.body : undefined,
    });
    const raw = await response.text();
    const contentType = response.headers.get("content-type") ?? "";
    let body: unknown = raw;
    if (contentType.includes("json") && raw) {
      try {
        body = JSON.parse(raw) as unknown;
      } catch {
        body = raw;
      }
    }

    return {
      status: response.status,
      statusText: response.statusText || (response.ok ? "OK" : "Error"),
      latencyMs: Math.max(1, Math.round(performance.now() - startedAt)),
      size: `${new Blob([raw]).size} B`,
      headers: Object.fromEntries(response.headers.entries()),
      body,
      raw,
    };
  } catch (error) {
    return networkError(error, Math.max(1, Math.round(performance.now() - startedAt)));
  }
}
