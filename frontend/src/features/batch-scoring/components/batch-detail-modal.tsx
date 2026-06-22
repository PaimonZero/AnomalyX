import { CheckCircle2, Clock3 } from "lucide-react";

import { RiskBadge } from "@/features/alerts/components/alert-badges";
import type { BatchResultRow } from "@/features/batch-scoring/types";
import { Badge } from "@/shared/ui/badge";
import { Modal } from "@/shared/ui/modal";

interface BatchDetailModalProps {
  row: BatchResultRow | null;
  batchName: string;
  onClose: () => void;
}

export function BatchDetailModal({ batchName, onClose, row }: BatchDetailModalProps) {
  const prediction = row?.prediction;

  return (
    <Modal
      open={Boolean(row && prediction)}
      onClose={onClose}
      size="lg"
      title={row && prediction ? (
        <span className="detail-title">
          <RiskBadge level={prediction.risk_level} />
          <code>Row {row.index + 1}</code>
          {prediction.is_flagged ? <Badge tone="critical">FLAGGED</Badge> : null}
        </span>
      ) : "Batch detail"}
      description={row?.transaction.transaction_id}
    >
      {row && prediction ? (
        <div className="batch-detail-grid">
          <section>
            <div className="batch-detail-score">
              <span>Risk score</span>
              <strong>{prediction.risk_score.toFixed(2)}</strong>
              <small>{prediction.model_version}</small>
            </div>

            <div className="context-grid">
              <div><span>Amount</span><strong>{new Intl.NumberFormat("en-US").format(row.transaction.amount)} {row.transaction.currency}</strong></div>
              <div><span>Channel</span><code>{row.transaction.channel}</code></div>
              <div><span>Sender</span><code>{row.transaction.sender_id.slice(0, 12)}…</code></div>
              <div><span>Receiver</span><code>{row.transaction.receiver_id.slice(0, 12)}…</code></div>
              <div className="context-grid__wide"><span>Timestamp</span><time>{row.transaction.timestamp}</time></div>
            </div>

            <div className="detail-section">
              <div className="section-label">Triggered rules</div>
              <div className="rule-cards">
                {prediction.triggered_rules.length ? prediction.triggered_rules.map((rule) => (
                  <div className="rule-card" key={rule.id}>
                    <code>{rule.id}</code>
                    <span>{rule.typology}</span>
                    <Badge tone="high">{rule.severity}</Badge>
                  </div>
                )) : <p className="batch-no-evidence">No rules triggered.</p>}
              </div>
            </div>
          </section>

          <section className="batch-detail-evidence">
            <div className="section-label">Top model features</div>
            <div className="feature-evidence-list">
              {prediction.top_features.map((feature) => (
                <div className="feature-evidence" key={feature.name}>
                  <div><code>{feature.name}</code><span>{String(feature.value)}</span></div>
                  <div className="contribution-track"><span style={{ width: `${Math.min(Math.abs(feature.contribution ?? 0) * 250, 100)}%` }} /></div>
                  <strong>{feature.contribution?.toFixed(2)}</strong>
                </div>
              ))}
            </div>

            <div className="batch-explanation">
              <div><Clock3 size={15} /> Explanation</div>
              <p>{prediction.explanation ?? "Explanation pending… The batch result returned before the explanation task finished."}</p>
            </div>

            <div className="batch-context-meta">
              <CheckCircle2 size={15} />
              <span>Batch: {batchName || "untitled"} · Alert: {prediction.alert_id ?? "none"}</span>
            </div>
          </section>
        </div>
      ) : null}
    </Modal>
  );
}
