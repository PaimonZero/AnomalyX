import type { AlertDetail, UpdateAlertStatusInput } from "@/features/alerts/types";
import { env } from "@/shared/config/env";
import { Button } from "@/shared/ui/button";
import { Modal } from "@/shared/ui/modal";

interface AlertActionDialogProps {
  alert: AlertDetail | null;
  action: "ESCALATED" | "DISMISSED" | null;
  error: string | null;
  submitting: boolean;
  onCancel: () => void;
  onConfirm: (input: UpdateAlertStatusInput) => void;
}

export function AlertActionDialog({ action, alert, error, onCancel, onConfirm, submitting }: AlertActionDialogProps) {
  if (!action || !alert) return null;
  const isEscalate = action === "ESCALATED";

  return (
    <Modal
      open
      onClose={onCancel}
      title={isEscalate ? "Escalate this alert?" : "Dismiss this alert?"}
      description={`${alert.id} · Risk ${alert.risk_score.toFixed(2)}`}
    >
      <div className="confirm-form">
        <p>
          {isEscalate
            ? "The backend will update this alert to ESCALATED and store the reviewer metadata."
            : "The backend will update this alert to DISMISSED and store the reviewer metadata."}
        </p>
        {error ? <div className="form-error">{error}</div> : null}
        <div className="confirm-actions">
          <Button variant="ghost" onClick={onCancel} disabled={submitting}>Cancel</Button>
          <Button
            variant={isEscalate ? "danger" : "primary"}
            disabled={submitting}
            onClick={() => onConfirm({ alertId: alert.id, status: action, reviewerId: env.reviewerId })}
          >
            {submitting ? "Updating…" : isEscalate ? "Confirm escalation" : "Confirm dismissal"}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
