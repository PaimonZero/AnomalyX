import { AlertTriangle, RotateCcw } from "lucide-react";

import {
  formatRuleTypology,
  summarizeRuleEngine,
  type RuleEngineDetails,
} from "@/features/monitoring/api/rules-detail-format";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { Modal } from "@/shared/ui/modal";

interface RuleEngineDetailModalProps {
  details: RuleEngineDetails | undefined;
  error: string | null;
  loading: boolean;
  open: boolean;
  reloadingRules: boolean;
  onClose: () => void;
  onReloadRules: () => void;
  onRetry: () => void;
}

function severityTone(severity: string): "success" | "warning" | "high" | "critical" {
  if (severity === "CRITICAL") return "critical";
  if (severity === "HIGH") return "high";
  if (severity === "MEDIUM") return "warning";
  return "success";
}

export function RuleEngineDetailModal(props: RuleEngineDetailModalProps) {
  return (
    <Modal
      open={props.open}
      onClose={props.onClose}
      size="lg"
      title="Rule engine details"
      description={props.details ? summarizeRuleEngine(props.details) : "Active backend rule configuration."}
    >
      <div className="rule-engine-detail">
        <div className="rule-engine-detail__toolbar">
          <span>{props.details ? `${props.details.rules.length} rules loaded from backend` : "Rules loaded from backend"}</span>
        </div>

        {props.loading ? (
          <div className="rule-engine-state">Loading rules…</div>
        ) : props.error ? (
          <div className="rule-engine-state rule-engine-state--error" role="alert">
            <AlertTriangle size={17} />
            <span>{props.error}</span>
            <Button size="sm" variant="secondary" onClick={props.onRetry}>
              Retry
            </Button>
          </div>
        ) : props.details ? (
          <>
            <div className="rule-engine-table-wrap">
              <table className="rule-engine-table">
                <thead>
                  <tr>
                    <th>Rule</th>
                    <th>Severity</th>
                    <th>Status</th>
                    <th>Recommended action</th>
                    <th>Condition</th>
                  </tr>
                </thead>
                <tbody>
                  {props.details.rules.map((rule) => (
                    <tr key={rule.id}>
                      <td>
                        <code>{rule.id}</code>
                        <small>{formatRuleTypology(rule)}</small>
                      </td>
                      <td>
                        <Badge tone={severityTone(rule.severity)}>{rule.severity}</Badge>
                      </td>
                      <td>{rule.enabled ? <Badge tone="success">ENABLED</Badge> : <Badge>DISABLED</Badge>}</td>
                      <td>
                        <code>{rule.action_hint ?? "—"}</code>
                      </td>
                      <td>
                        <code>{rule.condition ?? "—"}</code>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="rule-engine-detail__footer">
              <p>If you changed <code>rules.yaml</code>, apply those changes to the backend.</p>
              <Button variant="secondary" size="sm" disabled={props.reloadingRules} onClick={props.onReloadRules}>
                <RotateCcw size={14} className={props.reloadingRules ? "spin" : ""} />
                {props.reloadingRules ? "Applying rules to backend…" : "Apply rules.yaml to backend"}
              </Button>
            </div>
          </>
        ) : null}
      </div>
    </Modal>
  );
}
