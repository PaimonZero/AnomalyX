import { getMonitoringHealth, getMonitoringMetrics } from "@/features/monitoring/api/monitoring-api";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle2, Cpu, Database, Loader2, RefreshCw, Server } from "lucide-react";
import type { Language } from "../../types";

export function HealthDemo({ language }: { language: Language; token: string }) {
  const healthQuery = useQuery({
    queryKey: ["presentation-health"],
    queryFn: getMonitoringHealth,
    refetchInterval: false,
  });

  const metricsQuery = useQuery({
    queryKey: ["presentation-metrics"],
    queryFn: getMonitoringMetrics,
    refetchInterval: false,
  });

  const labels = {
    serviceStatus: language === "vi" ? "Trạng thái Dịch vụ" : "Service Status",
    modelInfo: language === "vi" ? "Thông tin Model" : "Model Info",
    keyMetrics: language === "vi" ? "Chỉ số Chính" : "Key Metrics",
    error: language === "vi" ? "Backend không khả dụng" : "Backend unavailable",
    up: language === "vi" ? "Hoạt động" : "Up",
    down: language === "vi" ? "Không hoạt động" : "Down",
    unknown: language === "vi" ? "Không rõ" : "Unknown",
    mock: language === "vi" ? "Mock" : "Mock",
    real: language === "vi" ? "Real" : "Real",
    version: language === "vi" ? "Version" : "Version",
    requests: language === "vi" ? "Requests" : "Requests",
    latency: language === "vi" ? "Latency" : "Latency",
    alerts: language === "vi" ? "Alerts" : "Alerts",
  };

  const isLoading = healthQuery.isLoading || metricsQuery.isLoading;
  const isError = healthQuery.isError && metricsQuery.isError;

  return (
    <div className="health-demo">
      <div className="health-demo-header">
        <h3>Observability</h3>
        <button
          className="button button--ghost button--sm"
          type="button"
          onClick={() => {
            healthQuery.refetch();
            metricsQuery.refetch();
          }}
          disabled={isLoading}
        >
          <RefreshCw size={16} className={isLoading ? "spin" : ""} />
        </button>
      </div>

      {isLoading && (
        <div className="health-demo-state">
          <Loader2 size={24} className="spin" />
        </div>
      )}

      {isError && (
        <div className="health-demo-state health-demo-state--error">
          <AlertTriangle size={20} />
          <span>{labels.error}</span>
        </div>
      )}

      {!isError && (
        <div className="health-demo-grid">
          {/* Service status cards */}
          <div className="health-demo-card">
            <div className="health-demo-card-header">
              <Server size={18} />
              <strong>{labels.serviceStatus}</strong>
            </div>
            <div className="health-demo-status-row">
              <span>API</span>
              {healthQuery.data ? (
                <span className="health-demo-badge health-demo-badge--up"><CheckCircle2 size={14} />{labels.up}</span>
              ) : (
                <span className="health-demo-badge health-demo-badge--down"><AlertTriangle size={14} />{labels.down}</span>
              )}
            </div>
            <div className="health-demo-status-row">
              <Database size={14} />
              <span>PostgreSQL</span>
              {healthQuery.data ? (
                <span className="health-demo-badge health-demo-badge--up"><CheckCircle2 size={14} />{labels.up}</span>
              ) : (
                <span className="health-demo-badge health-demo-badge--down"><AlertTriangle size={14} />{labels.down}</span>
              )}
            </div>
            <div className="health-demo-status-row">
              <Database size={14} />
              <span>Redis</span>
              {healthQuery.data ? (
                <span className="health-demo-badge health-demo-badge--up"><CheckCircle2 size={14} />{labels.up}</span>
              ) : (
                <span className="health-demo-badge health-demo-badge--down"><AlertTriangle size={14} />{labels.down}</span>
              )}
            </div>
          </div>

          {/* Model card */}
          <div className="health-demo-card">
            <div className="health-demo-card-header">
              <Cpu size={18} />
              <strong>{labels.modelInfo}</strong>
            </div>
            {healthQuery.data && (
              <>
                <div className="health-demo-status-row">
                  <span>{labels.version}</span>
                  <span className="mono" style={{ fontSize: "0.75rem" }}>
                    {healthQuery.data.model?.version ?? labels.unknown}
                  </span>
                </div>
                <div className="health-demo-status-row">
                  <span>Mode</span>
                  <span className={`badge ${healthQuery.data.model?.mock_enabled !== false ? "badge--warning" : "badge--success"}`}>
                    {healthQuery.data.model?.mock_enabled !== false ? labels.mock : labels.real}
                  </span>
                </div>
              </>
            )}
          </div>

          {/* Metrics card */}
          <div className="health-demo-card">
            <div className="health-demo-card-header">
              <BarChartIcon />
              <strong>{labels.keyMetrics}</strong>
            </div>
            {metricsQuery.data && (
              <>
                <div className="health-demo-metric">
                  <span>{labels.requests}</span>
                  <strong>{metricsQuery.data.requestsTotal ?? "—"}</strong>
                </div>
                <div className="health-demo-metric">
                  <span>{labels.latency}</span>
                  <strong>{metricsQuery.data.requestP95Ms != null ? `${(metricsQuery.data.requestP95Ms / 1000).toFixed(3)}s` : "—"}</strong>
                </div>
                <div className="health-demo-metric">
                  <span>{labels.alerts}</span>
                  <strong>{metricsQuery.data.alertsTotal ?? "—"}</strong>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function BarChartIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="20" x2="18" y2="10" />
      <line x1="12" y1="20" x2="12" y2="4" />
      <line x1="6" y1="20" x2="6" y2="14" />
    </svg>
  );
}
