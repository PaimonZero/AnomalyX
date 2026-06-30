import { listAlerts } from "@/features/alerts/api/alerts-api";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, ChevronDown, ChevronUp, Loader2, RefreshCw } from "lucide-react";
import { useState } from "react";
import type { Language } from "../../types";

export function AlertsDemo({ language, token }: { language: Language; token: string }) {
  const [expanded, setExpanded] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const { data: alerts, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ["presentation-alerts", token],
    queryFn: () =>
      listAlerts({ status: "ALL", search: "", risk: "ALL", source: "ALL", sort: "risk_desc" }, token),
    refetchInterval: autoRefresh ? 10_000 : false,
    enabled: !!token,
    retry: 1,
  });

  const labels = {
    title: language === "vi" ? "Cảnh báo Gần đây" : "Recent Alerts",
    loading: language === "vi" ? "Đang tải..." : "Loading...",
    error: language === "vi" ? "Backend không khả dụng. Khởi động với docker compose up." : "Backend unavailable. Start with docker compose up.",
    empty: language === "vi" ? "Chưa có cảnh báo nào. Gửi một giao dịch đáng ngờ trước." : "No alerts yet. Submit a suspicious transaction first.",
    autoRefresh: language === "vi" ? "Tự động" : "Auto",
    id: language === "vi" ? "Alert ID" : "Alert ID",
    txId: language === "vi" ? "TX ID" : "TX ID",
    risk: language === "vi" ? "Risk" : "Risk",
    status: language === "vi" ? "Trạng thái" : "Status",
    source: language === "vi" ? "Nguồn" : "Source",
    date: language === "vi" ? "Thời gian" : "Date",
    rules: language === "vi" ? "Rule" : "Rules",
    features: language === "vi" ? "Features" : "Features",
    explanation: language === "vi" ? "Giải thích" : "Explanation",
  };

  const statusLabels: Record<string, { vi: string; en: string }> = {
    NEW: { vi: "Mới", en: "New" },
    ESCALATED: { vi: "Đã leo thang", en: "Escalated" },
    DISMISSED: { vi: "Đã bỏ qua", en: "Dismissed" },
  };

  return (
    <div className="alerts-demo">
      <div className="alerts-demo-header">
        <h3>{labels.title}</h3>
        <div className="alerts-demo-actions">
          <label className="alerts-demo-refresh-label">
            <input type="checkbox" checked={autoRefresh} onChange={(e) => setAutoRefresh(e.target.checked)} />
            <span>{labels.autoRefresh}</span>
          </label>
          <button className="button button--ghost button--sm" type="button" onClick={() => refetch()} disabled={isFetching}>
            <RefreshCw size={16} className={isFetching ? "spin" : ""} />
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="alerts-demo-state">
          <Loader2 size={24} className="spin" />
          <span>{labels.loading}</span>
        </div>
      )}

      {isError && (
        <div className="alerts-demo-state alerts-demo-state--error">
          <AlertTriangle size={20} />
          <span>{labels.error}</span>
        </div>
      )}

      {alerts && alerts.length === 0 && (
        <div className="alerts-demo-state">
          <span>{labels.empty}</span>
        </div>
      )}

      {alerts && alerts.length > 0 && (
        <div className="alerts-demo-table-wrap">
          <table className="alerts-demo-table">
            <thead>
              <tr>
                <th>{labels.id}</th>
                <th>{labels.txId}</th>
                <th>{labels.risk}</th>
                <th>{labels.status}</th>
                <th>{labels.source}</th>
                <th>{labels.date}</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {alerts.slice(0, 10).map((alert) => (
                <>
                  <tr
                    key={alert.id}
                    className="alerts-demo-row"
                    onClick={() => setExpanded(expanded === alert.id ? null : alert.id)}
                  >
                    <td className="mono">{alert.id}</td>
                    <td className="mono">{alert.transaction_id.slice(0, 16)}…</td>
                    <td>
                      <span className={`badge badge--${alert.risk_level.toLowerCase() === "critical" ? "critical" : alert.risk_level.toLowerCase() === "high" ? "high" : alert.risk_level.toLowerCase() === "medium" ? "warning" : "success"}`}>
                        {alert.risk_level}
                      </span>
                    </td>
                    <td>
                      <span className={`badge badge--${alert.status === "NEW" ? "info" : alert.status === "ESCALATED" ? "critical" : "neutral"}`}>
                        {statusLabels[alert.status]?.[language] ?? alert.status}
                      </span>
                    </td>
                    <td>{alert.explanation_source ?? "—"}</td>
                    <td className="mono">{new Date(alert.created_at).toLocaleDateString()}</td>
                    <td>{expanded === alert.id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}</td>
                  </tr>
                  {expanded === alert.id && (
                    <tr key={`${alert.id}-detail`} className="alerts-demo-detail-row">
                      <td colSpan={7}>
                        <div className="alerts-demo-detail">
                          {alert.triggered_rules.length > 0 && (
                            <div>
                              <strong>{labels.rules}:</strong>
                              <div className="alerts-demo-tags">
                                {alert.triggered_rules.map((r) => (
                                  <span key={r.id} className="badge badge--neutral">{r.id}</span>
                                ))}
                              </div>
                            </div>
                          )}
                          {alert.top_features.length > 0 && (
                            <div>
                              <strong>{labels.features}:</strong>
                              <div className="alerts-demo-tags">
                                {alert.top_features.slice(0, 5).map((f) => (
                                  <span key={f.name} className="mono" style={{ fontSize: "0.7rem" }}>
                                    {f.name}={typeof f.value === "number" ? f.value.toFixed(3) : String(f.value)}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          {alert.explanation && (
                            <div>
                              <strong>{labels.explanation}:</strong>
                              <p className="alerts-demo-explanation">{alert.explanation}</p>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
