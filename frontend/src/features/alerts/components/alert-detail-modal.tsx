import { ArrowUpCircle, Clock3, ShieldCheck, XCircle } from "lucide-react";

import { RiskBadge, SourceBadge, StatusBadge } from "@/features/alerts/components/alert-badges";
import type { AlertDetail } from "@/features/alerts/types";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { Modal } from "@/shared/ui/modal";

interface AlertDetailModalProps {
  alert: AlertDetail | null;
  loading: boolean;
  error: string | null;
  onClose: () => void;
  onAction: (alert: AlertDetail, action: "ESCALATED" | "DISMISSED") => void;
}

const formatAmount = (value: number, currency: string) =>
  `${new Intl.NumberFormat("en-US").format(value)} ${currency}`;

const formatTimestamp = (value: string) =>
  new Intl.DateTimeFormat("en-US", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));

export function AlertDetailModal({ alert, error, loading, onAction, onClose }: AlertDetailModalProps) {
  return (
    <Modal
      open={alert !== null || loading || Boolean(error)}
      onClose={onClose}
      size="lg"
      title={alert ? <span className="detail-title"><RiskBadge level={alert.risk_level} /> <code>{alert.id}</code> <StatusBadge status={alert.status} /></span> : "Alert detail"}
      description="Risk evidence and decision explanation"
    >
      {loading && !alert ? (
        <div className="detail-loading" role="status">Loading alert detail…</div>
      ) : error && !alert ? (
        <div className="detail-error" role="alert">{error}</div>
      ) : alert ? (
        <div className="alert-detail-grid">
          <div className="detail-column detail-column--evidence">
            <section className="risk-summary">
              <div>
                <span>Risk score</span>
                <strong>{Math.round(alert.risk_score * 100)}<small>%</small></strong>
              </div>
              <dl>
                {alert.model_version ? <div><dt>Model</dt><dd>{alert.model_version}</dd></div> : null}
                <div><dt>Flagged</dt><dd><Badge tone="critical">YES</Badge></dd></div>
                {alert.channel ? <div><dt>Channel</dt><dd><Badge>{alert.channel}</Badge></dd></div> : null}
              </dl>
            </section>

            <section className="detail-section">
              <div className="section-label"><ShieldCheck size={14} /> Alert context</div>
              <div className="context-grid context-grid--compact">
                <div><span>Transaction</span><code>{alert.transaction_id.slice(0, 18)}…</code></div>
                <div><span>Alert</span><code>{alert.id}</code></div>
                {alert.amount !== undefined && alert.currency ? <div><span>Amount</span><strong>{formatAmount(alert.amount, alert.currency)}</strong></div> : null}
                {alert.sender_id ? <div><span>Sender</span><code>{alert.sender_id.slice(0, 8)}…</code></div> : null}
                {alert.receiver_id ? <div><span>Receiver</span><code>{alert.receiver_id.slice(0, 8)}…</code></div> : null}
                <div><span>Created</span><time>{formatTimestamp(alert.transaction_timestamp ?? alert.created_at)}</time></div>
              </div>
            </section>

            <section className="detail-section">
              <div className="section-label">Triggered rules</div>
              <div className="rule-cards">
                {alert.triggered_rules.length ? alert.triggered_rules.map((rule) => (
                  <div className="rule-card" key={rule.id}>
                    <code>{rule.id}</code>
                    <span>{rule.typology?.replaceAll("_", " ")}</span>
                    <Badge tone={rule.severity === "HIGH" || rule.severity === "CRITICAL" ? "high" : "warning"}>{rule.severity}</Badge>
                  </div>
                )) : <p className="detail-empty-copy">No rule evidence.</p>}
              </div>
            </section>

            <section className="detail-section">
              <div className="section-label">Top model features</div>
              <div className="feature-evidence-list">
                {alert.top_features.length ? alert.top_features.map((feature) => {
                  const contribution = feature.contribution ?? 0;
                  return (
                    <div className="feature-evidence" key={feature.name}>
                      <div><code>{feature.name}</code><span>{String(feature.value)}</span></div>
                      <div className="contribution-track"><span style={{ width: `${Math.min(Math.abs(contribution) * 250, 100)}%` }} /></div>
                      <strong>{contribution >= 0 ? "+" : ""}{contribution.toFixed(2)}</strong>
                    </div>
                  );
                }) : <p className="detail-empty-copy">No feature evidence.</p>}
              </div>
            </section>
          </div>

          <div className="detail-column detail-column--explanation">
            <section className="explanation-panel">
              <div className="explanation-heading"><span>Explanation</span><SourceBadge source={alert.explanation_source} /></div>
              {alert.explanation ? <p>{alert.explanation}</p> : <div className="pending-copy"><span /> Generating explanation…</div>}
              {alert.explanation_source === "template" ? <small>LLM is unavailable, so a deterministic rule summary is shown.</small> : null}
            </section>

            <section className="audit-panel">
              <div className="section-label"><Clock3 size={14} /> Audit metadata</div>
              <dl>
                <div><dt>Reviewer</dt><dd>{alert.reviewer_id ?? "Unassigned"}</dd></div>
                <div><dt>Created</dt><dd>{formatTimestamp(alert.created_at)}</dd></div>
                <div><dt>Updated</dt><dd>{formatTimestamp(alert.updated_at)}</dd></div>
              </dl>
            </section>

            <div className="detail-actions">
              <Button variant="danger" disabled={alert.status === "ESCALATED"} onClick={() => onAction(alert, "ESCALATED")}>
                <ArrowUpCircle size={16} /> Escalate
              </Button>
              <Button variant="secondary" disabled={alert.status === "DISMISSED"} onClick={() => onAction(alert, "DISMISSED")}>
                <XCircle size={16} /> Dismiss
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </Modal>
  );
}
