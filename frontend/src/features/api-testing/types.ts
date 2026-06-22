export type HttpMethod = "GET" | "POST" | "PATCH";

export interface EndpointDefinition {
  id: string;
  method: HttpMethod;
  path: string;
  auth: boolean;
  description: string;
}

export interface ApiTestRequest {
  endpoint: EndpointDefinition;
  token: string;
  pathParam: string;
  query: Record<string, string>;
  body: string;
}

export interface ApiTestResponse {
  status: number;
  statusText: string;
  latencyMs: number;
  size: string;
  headers: Record<string, string>;
  body: unknown;
  raw: string;
}
