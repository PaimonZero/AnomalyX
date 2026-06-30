import { apiRequest } from "@/shared/api/client";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, ChevronDown, ChevronUp, Loader2, RefreshCw } from "lucide-react";
import { useState } from "react";
import type { Language } from "../../types";

interface RuleEntry {
  id: string;
  typology?: string | null;
  severity?: string;
  enabled?: boolean;
  condition?: unknown;
  action?: unknown;
}

export function RulesDemo({ language, token }: { language: Language; token: string }) {
  const [expanded, setExpanded] = useState<string | null>(null);

  const { data: rules, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ["presentation-rules", token],
    queryFn: () => apiRequest<{ rules: RuleEntry[] }>("/rules", { token }),
    enabled: !!token,
    retry: 1,
  });

  const labels = {
    title: language === "vi" ? "Active Rules" : "Active Rules",
    loading: language === "vi" ? "Đang tải..." : "Loading...",
    error: language === "vi" ? "Backend không khả dụng. Khởi động với docker compose up." : "Backend unavailable. Start with docker compose up.",
    empty: language === "vi" ? "Không có rule nào được tải." : "No rules loaded.",
    id: language === "vi" ? "Rule ID" : "Rule ID",
    typology: language === "vi" ? "Typology" : "Typology",
    severity: language === "vi" ? "Mức độ" : "Severity",
    enabled: language === "vi" ? "Bật" : "Enabled",
    disabled: language === "vi" ? "Tắt" : "Disabled",
    condition: language === "vi" ? "Điều kiện" : "Condition",
    action: language === "vi" ? "Hành động" : "Action",
  };

  const ruleList = rules?.rules ?? [];

  return (
    <div className="rules-demo">
      <div className="rules-demo-header">
        <h3>{labels.title}</h3>
        <button className="button button--ghost button--sm" type="button" onClick={() => refetch()} disabled={isFetching}>
          <RefreshCw size={16} className={isFetching ? "spin" : ""} />
        </button>
      </div>

      {isLoading && (
        <div className="rules-demo-state">
          <Loader2 size={24} className="spin" />
          <span>{labels.loading}</span>
        </div>
      )}

      {isError && (
        <div className="rules-demo-state rules-demo-state--error">
          <AlertTriangle size={20} />
          <span>{labels.error}</span>
        </div>
      )}

      {!isLoading && !isError && ruleList.length === 0 && (
        <div className="rules-demo-state">
          <span>{labels.empty}</span>
        </div>
      )}

      {!isLoading && !isError && ruleList.length > 0 && (
        <div className="rules-demo-table-wrap">
          <table className="rules-demo-table">
            <thead>
              <tr>
                <th>{labels.id}</th>
                <th>{labels.typology}</th>
                <th>{labels.severity}</th>
                <th>{labels.enabled}</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {ruleList.map((rule) => (
                <>
                  <tr
                    key={rule.id}
                    className="rules-demo-row"
                    onClick={() => setExpanded(expanded === rule.id ? null : rule.id)}
                  >
                    <td className="mono">{rule.id}</td>
                    <td>{rule.typology ?? "—"}</td>
                    <td>
                      <span className={`badge badge--${rule.severity?.toLowerCase() === "critical" ? "critical" : rule.severity?.toLowerCase() === "high" ? "high" : "neutral"}`}>
                        {rule.severity ?? "—"}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${rule.enabled !== false ? "badge--success" : "badge--neutral"}`}>
                        {rule.enabled !== false ? labels.enabled : labels.disabled}
                      </span>
                    </td>
                    <td>{expanded === rule.id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}</td>
                  </tr>
                  {expanded === rule.id && (
                    <tr key={`${rule.id}-detail`} className="rules-demo-detail-row">
                      <td colSpan={5}>
                        <div className="rules-demo-detail">
                          <div>
                            <strong>{labels.condition}:</strong>
                            <pre className="rules-demo-code">{JSON.stringify(rule.condition, null, 2)}</pre>
                          </div>
                          {rule.action != null && (
                            <div>
                              <strong>{labels.action}:</strong>
                              <pre className="rules-demo-code">{JSON.stringify(rule.action, null, 2)}</pre>
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
