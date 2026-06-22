import { ChevronRight, Copy } from "lucide-react";

import { RiskBadge, SourceBadge, StatusBadge } from "@/features/alerts/components/alert-badges";
import type { AlertDetail } from "@/features/alerts/types";
import { Button } from "@/shared/ui/button";

interface AlertsTableProps {
  alerts: AlertDetail[];
  loading: boolean;
  onOpen: (alert: AlertDetail) => void;
  onClearFilters: () => void;
}

function truncateId(value: string) {
  return `${value.slice(0, 8)}…`;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

async function copyId(value: string) {
  await navigator.clipboard.writeText(value);
}

export function AlertsTable({ alerts, loading, onClearFilters, onOpen }: AlertsTableProps) {
  return (
    <div className="alerts-table-card">
      <div className="table-heading">
        <div>
          <h2>Review queue</h2>
          <p>Shows HIGH and CRITICAL flagged transactions only.</p>
        </div>
        <span>{loading ? "Loading" : `${alerts.length} alerts`}</span>
      </div>

      <div className="table-scroll">
        <table className="alerts-table">
          <thead>
            <tr>
              <th>Alert / Transaction</th>
              <th>Risk</th>
              <th>Status</th>
              <th>Triggered rules</th>
              <th>Explanation</th>
              <th>Updated</th>
              <th><span className="sr-only">Open detail</span></th>
            </tr>
          </thead>
          <tbody>
            {loading
              ? Array.from({ length: 6 }, (_, index) => (
                  <tr key={index} className="skeleton-row">
                    <td colSpan={7}><span /></td>
                  </tr>
                ))
              : alerts.map((alert) => (
                  <tr key={alert.id} className={`alert-row alert-row--${alert.risk_level.toLowerCase()}`} onClick={() => onOpen(alert)}>
                    <td>
                      <div className="id-stack">
                        <strong>{alert.id}</strong>
                        <span title={alert.transaction_id}>{truncateId(alert.transaction_id)}</span>
                        <button
                          className="copy-button"
                          type="button"
                          aria-label={`Copy ${alert.transaction_id}`}
                          onClick={(event) => {
                            event.stopPropagation();
                            void copyId(alert.transaction_id);
                          }}
                        >
                          <Copy size={12} />
                        </button>
                      </div>
                    </td>
                    <td>
                      <div className="risk-cell">
                        <strong>{alert.risk_score.toFixed(2)}</strong>
                        <RiskBadge level={alert.risk_level} />
                      </div>
                    </td>
                    <td><StatusBadge status={alert.status} /></td>
                    <td>
                      <div className="rule-list-inline">
                        {alert.triggered_rules.map((rule) => <code key={rule.id}>{rule.id}</code>)}
                      </div>
                    </td>
                    <td><SourceBadge source={alert.explanation_source} /></td>
                    <td><time title={alert.updated_at}>{formatDate(alert.updated_at)}</time></td>
                    <td>
                      <div className="row-actions">
                        <ChevronRight size={16} className="row-chevron" />
                      </div>
                    </td>
                  </tr>
                ))}
          </tbody>
        </table>
      </div>

      {!loading && alerts.length === 0 ? (
        <div className="empty-state">
          <p>No alerts match the current filters.</p>
          <Button variant="secondary" size="sm" onClick={onClearFilters}>Clear filters</Button>
        </div>
      ) : null}
    </div>
  );
}
