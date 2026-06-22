import type { PredictionResponse, TransactionRequest } from "@/shared/types/api";

export interface BatchValidationError {
  index: number;
  transactionId?: string;
  field: string;
  message: string;
}

export interface BatchValidationResult {
  transactions: TransactionRequest[];
  errors: BatchValidationError[];
}

export interface BatchResultRow {
  index: number;
  transaction: TransactionRequest;
  prediction?: PredictionResponse;
  error?: {
    code: string;
    message: string;
  };
}

export interface BatchPredictionError {
  index: number;
  transaction_id?: string | null;
  code: string;
  message: string;
}

export interface BatchPredictionResult {
  index: number;
  transaction_id?: string | null;
  prediction?: PredictionResponse | null;
  error?: BatchPredictionError | null;
}

export interface BatchScoreResponse {
  batch_id?: string | null;
  total_transactions: number;
  flagged_count: number;
  predictions: PredictionResponse[];
  flagged_predictions: PredictionResponse[];
  errors: BatchPredictionError[];
  results: BatchPredictionResult[];
  alert_ids: string[];
}
