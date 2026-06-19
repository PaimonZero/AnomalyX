export interface MonitoringHealth {
  status: "ok" | "degraded";
  app: string;
  environment: string;
  timestamp: string;
  checks: Record<string, boolean>;
  storage: {
    alert_repository: string;
    idempotency_store: string;
  };
  model: {
    mock_enabled: boolean;
    version: string;
  };
  metrics_enabled: boolean;
}

export interface MetricSeriesPoint {
  label: string;
  value: number;
}

export interface MonitoringMetrics {
  requestsTotal: number;
  requestSuccessRate: number;
  requestP95Ms: number;
  alertsTotal: number;
  decisions: Record<"LOW" | "MEDIUM" | "HIGH" | "CRITICAL", number>;
  httpStatuses: Record<"2xx" | "4xx" | "5xx", number>;
  ruleTriggers: Array<{ id: string; severity: "HIGH" | "MEDIUM"; count: number }>;
  explanationOutcomes: { llm: number; template: number };
  explanationP95Ms: number;
  fallbackTotal: number;
  driftPlaceholder: number;
  requestVolume: MetricSeriesPoint[];
  latencyTrend: MetricSeriesPoint[];
  scrapedAt: string;
}

