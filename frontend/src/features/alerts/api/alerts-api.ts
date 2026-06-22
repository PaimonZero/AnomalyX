import type { Alert } from "@/shared/types/api";
import { apiRequest } from "@/shared/api/client";
import type { AlertDetail, AlertFilters, UpdateAlertStatusInput } from "@/features/alerts/types";

function normalizeAlert(alert: Alert): AlertDetail {
  return {
    ...alert,
    is_flagged: true,
    explanation_source:
      alert.explanation_source === "llm" || alert.explanation_source === "template"
        ? alert.explanation_source
        : "pending",
  };
}

function filterAndSortAlerts(alerts: AlertDetail[], filters: AlertFilters) {
  const search = filters.search.trim().toLowerCase();

  return alerts
    .filter((alert) => {
      const matchesSearch =
        !search ||
        alert.id.toLowerCase().includes(search) ||
        alert.transaction_id.toLowerCase().includes(search);
      const matchesRisk = filters.risk === "ALL" || alert.risk_level === filters.risk;
      const matchesSource = filters.source === "ALL" || alert.explanation_source === filters.source;
      return matchesSearch && matchesRisk && matchesSource;
    })
    .sort((left, right) =>
      filters.sort === "risk_desc"
        ? right.risk_score - left.risk_score
        : Date.parse(right.updated_at) - Date.parse(left.updated_at),
    );
}

export async function listAlerts(filters: AlertFilters, token: string): Promise<AlertDetail[]> {
  const query = filters.status === "ALL" ? "" : `?status=${encodeURIComponent(filters.status)}`;
  const alerts = await apiRequest<Alert[]>(`/alerts${query}`, { token });
  return filterAndSortAlerts(alerts.map(normalizeAlert), filters);
}

export async function getAlert(alertId: string, token: string): Promise<AlertDetail> {
  const alert = await apiRequest<Alert>(`/alerts/${encodeURIComponent(alertId)}`, {
    token,
  });
  return normalizeAlert(alert);
}

export async function updateAlertStatus(input: UpdateAlertStatusInput, token: string): Promise<AlertDetail> {
  const alert = await apiRequest<Alert>(`/alerts/${encodeURIComponent(input.alertId)}/status`, {
    method: "PATCH",
    token,
    body: {
      status: input.status,
      reviewer_id: input.reviewerId,
    },
  });
  return normalizeAlert(alert);
}
