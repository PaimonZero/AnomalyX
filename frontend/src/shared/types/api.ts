export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type AlertStatus = "NEW" | "ESCALATED" | "DISMISSED";
export type TransactionChannel = "PAYMENT" | "TRANSFER" | "CASH_OUT" | "CASH_IN" | "DEBIT";

export interface TriggeredRule {
  id: string;
  severity: "MINOR" | "MEDIUM" | "HIGH" | "CRITICAL";
  typology?: string | null;
}

export interface TopFeature {
  name: string;
  value: number | string | boolean;
  contribution?: number | null;
}

export interface TransactionRequest {
  transaction_id: string;
  sender_id: string;
  receiver_id: string;
  sender_balance: number;
  receiver_balance: number;
  amount: number;
  currency: string;
  timestamp: string;
  channel: TransactionChannel;
  device_id?: string;
  location_country?: string;
  location_region?: string;
}

export interface PredictionResponse {
  transaction_id: string;
  risk_score: number;
  risk_level: RiskLevel;
  is_flagged: boolean;
  model_version: string;
  triggered_rules: TriggeredRule[];
  top_features: TopFeature[];
  explanation?: string | null;
  explanation_source?: string | null;
  alert_id?: string | null;
}

export interface Alert {
  id: string;
  transaction_id: string;
  risk_score: number;
  risk_level: RiskLevel;
  status: AlertStatus;
  triggered_rules: TriggeredRule[];
  top_features: TopFeature[];
  explanation?: string | null;
  explanation_source?: string | null;
  reviewer_id?: string | null;
  reviewed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApiErrorEnvelope {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}

