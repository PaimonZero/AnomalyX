import type { HttpMethod } from "@/features/api-testing/types";

interface BuildIntegrationSampleInput {
  apiBaseUrl: string;
  endpointPath: string;
  method: HttpMethod;
  token: string;
  body: string;
}

function joinEndpoint(apiBaseUrl: string, endpointPath: string) {
  const base = apiBaseUrl.replace(/\/$/, "");

  if (!base) return endpointPath;
  if (base.endsWith("/api/v1") && endpointPath.startsWith("/api/v1/")) {
    return `${base.slice(0, -"/api/v1".length)}${endpointPath}`;
  }
  if (base === "/api/v1" && endpointPath.startsWith("/api/v1/")) {
    return endpointPath;
  }

  return `${base}${endpointPath.startsWith("/") ? endpointPath : `/${endpointPath}`}`;
}

function escapeSingleQuotedShell(value: string) {
  return value.replaceAll("'", "'\"'\"'");
}

export function buildIntegrationSample(input: BuildIntegrationSampleInput) {
  const endpoint = joinEndpoint(input.apiBaseUrl, input.endpointPath);
  const authToken = input.token.trim() || "<AUTH_TOKEN>";
  const jsonBody = input.body.trim() || "{}";
  const curl = [
    `curl -X ${input.method} "${endpoint}"`,
    `  -H "Authorization: Bearer ${authToken}"`,
    `  -H "Content-Type: application/json"`,
    `  -d '${escapeSingleQuotedShell(jsonBody)}'`,
  ].join(" \\\n");

  return {
    authToken,
    curl,
    endpoint,
    jsonBody,
  };
}
