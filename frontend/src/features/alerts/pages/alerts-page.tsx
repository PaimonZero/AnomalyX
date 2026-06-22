import { AlertTriangle, Clock3, ShieldAlert, ShieldCheck } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { AlertActionDialog } from "@/features/alerts/components/alert-action-dialog";
import { AlertDetailModal } from "@/features/alerts/components/alert-detail-modal";
import { AlertsTable } from "@/features/alerts/components/alerts-table";
import { AlertsToolbar } from "@/features/alerts/components/alerts-toolbar";
import { useAlertDetail, useAlerts, useUpdateAlertStatus } from "@/features/alerts/hooks/use-alerts";
import type { AlertDetail, AlertFilters } from "@/features/alerts/types";
import { ApiError } from "@/shared/api/client";
import { Button } from "@/shared/ui/button";

const defaultFilters: AlertFilters = {
  search: "",
  status: "ALL",
  risk: "ALL",
  source: "ALL",
  sort: "risk_desc",
};

interface PendingAction {
  alert: AlertDetail;
  action: "ESCALATED" | "DISMISSED";
}

export function AlertsPage() {
  const [filters, setFilters] = useState(defaultFilters);
  const [selectedAlertId, setSelectedAlertId] = useState<string | null>(null);
  const [pendingAction, setPendingAction] = useState<PendingAction | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const alertsQuery = useAlerts(filters);
  const alertDetailQuery = useAlertDetail(selectedAlertId);
  const updateStatus = useUpdateAlertStatus();

  const alerts = useMemo(() => alertsQuery.data ?? [], [alertsQuery.data]);
  const selectedAlert =
    alertDetailQuery.data ??
    alerts.find((alert) => alert.id === selectedAlertId) ??
    pendingAction?.alert ??
    null;
  const stats = useMemo(
    () => ({
      newCount: alerts.filter((alert) => alert.status === "NEW").length,
      criticalCount: alerts.filter((alert) => alert.risk_level === "CRITICAL").length,
      escalatedCount: alerts.filter((alert) => alert.status === "ESCALATED").length,
      pendingCount: alerts.filter((alert) => alert.explanation_source === "pending").length,
    }),
    [alerts],
  );

  useEffect(() => {
    if (!toast) return;
    const timeout = window.setTimeout(() => setToast(null), 3200);
    return () => window.clearTimeout(timeout);
  }, [toast]);

  const openAction = (alert: AlertDetail, action: PendingAction["action"]) => {
    updateStatus.reset();
    setPendingAction({ alert, action });
  };

  return (
    <div className="alerts-page">
      <section className="alerts-overview" aria-label="Alert overview">
        <article>
          <div className="stat-icon stat-icon--info"><ShieldAlert size={17} /></div>
          <span>Pending review</span>
          <strong>{alertsQuery.isLoading ? "—" : stats.newCount}</strong>
          <small>Needs reviewer action</small>
        </article>
        <article>
          <div className="stat-icon stat-icon--critical"><AlertTriangle size={17} /></div>
          <span>Critical</span>
          <strong>{alertsQuery.isLoading ? "—" : stats.criticalCount}</strong>
          <small>Investigation priority</small>
        </article>
        <article>
          <div className="stat-icon stat-icon--success"><ShieldCheck size={17} /></div>
          <span>Escalated</span>
          <strong>{alertsQuery.isLoading ? "—" : stats.escalatedCount}</strong>
          <small>Review label created</small>
        </article>
        <article>
          <div className="stat-icon stat-icon--warning"><Clock3 size={17} /></div>
          <span>Pending explanation</span>
          <strong>{alertsQuery.isLoading ? "—" : stats.pendingCount}</strong>
          <small>LLM task in progress</small>
        </article>
      </section>

      <AlertsToolbar filters={filters} onChange={setFilters} onClear={() => setFilters(defaultFilters)} />

      {alertsQuery.isError ? (
        <div className="alerts-error" role="alert">
          <div>
            <AlertTriangle size={17} />
            <span>
              {alertsQuery.error instanceof ApiError
                ? `${alertsQuery.error.code}: ${alertsQuery.error.message}`
                : "Could not load alerts from the backend."}
            </span>
          </div>
          <Button size="sm" onClick={() => void alertsQuery.refetch()}>Retry</Button>
        </div>
      ) : (
        <AlertsTable
          alerts={alerts}
          loading={alertsQuery.isLoading}
          onOpen={(alert) => setSelectedAlertId(alert.id)}
          onClearFilters={() => setFilters(defaultFilters)}
          onCopyFeedback={setToast}
        />
      )}

      <AlertDetailModal
        alert={selectedAlertId ? selectedAlert : null}
        loading={alertDetailQuery.isLoading}
        error={alertDetailQuery.error instanceof Error ? alertDetailQuery.error.message : null}
        onClose={() => setSelectedAlertId(null)}
        onAction={openAction}
      />

      <AlertActionDialog
        alert={pendingAction?.alert ?? null}
        action={pendingAction?.action ?? null}
        error={updateStatus.error instanceof Error ? updateStatus.error.message : null}
        submitting={updateStatus.isPending}
        onCancel={() => {
          if (!updateStatus.isPending) setPendingAction(null);
        }}
        onConfirm={(input) => {
          updateStatus.mutate(input, {
            onSuccess: () => {
              const verb = input.status === "ESCALATED" ? "escalated" : "dismissed";
              setToast(`${input.alertId} was ${verb}.`);
              setPendingAction(null);
              setSelectedAlertId(null);
            },
          });
        }}
      />

      {toast ? <div className="toast" role="status"><ShieldCheck size={17} />{toast}</div> : null}
    </div>
  );
}
