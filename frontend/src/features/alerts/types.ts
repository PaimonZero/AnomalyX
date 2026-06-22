import type { Alert, AlertStatus, TransactionChannel } from "@/shared/types/api";

export type ExplanationSource = "llm" | "template" | "pending";

export interface AlertDetail extends Alert {
  is_flagged: true;
  model_version?: string;
  amount?: number;
  currency?: string;
  channel?: TransactionChannel;
  transaction_timestamp?: string;
  sender_id?: string;
  receiver_id?: string;
  explanation_source: ExplanationSource;
}

export interface AlertFilters {
  search: string;
  status: AlertStatus | "ALL";
  risk: "HIGH" | "CRITICAL" | "ALL";
  source: ExplanationSource | "ALL";
  sort: "risk_desc" | "updated_desc";
}

export interface UpdateAlertStatusInput {
  alertId: string;
  status: Exclude<AlertStatus, "NEW">;
  reviewerId: string;
}
