import { parseMonitoringMetrics } from "@/features/monitoring/api/prometheus-parser";
import type { MonitoringHealth, MonitoringMetrics } from "@/features/monitoring/types";
import { ApiError, apiRequest } from "@/shared/api/client";
import { env } from "@/shared/config/env";

export async function getMonitoringHealth(): Promise<MonitoringHealth> {
  return apiRequest<MonitoringHealth>("/health");
}

export async function getMonitoringMetrics(): Promise<MonitoringMetrics> {
  let response: Response;
  try {
    response = await fetch(`${env.apiBaseUrl}/metrics`, {
      headers: { Accept: "text/plain" },
    });
  } catch (error) {
    throw new ApiError(
      0,
      "NETWORK_ERROR",
      `Cannot connect to API at ${env.apiBaseUrl}.`,
      error instanceof Error ? error.message : undefined,
    );
  }

  if (!response.ok) {
    throw new ApiError(response.status, "HTTP_ERROR", `Request failed with status ${response.status}`);
  }

  return parseMonitoringMetrics(await response.text());
}
