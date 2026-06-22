import type { TransactionRequest } from "@/shared/types/api";
import { apiRequest } from "@/shared/api/client";
import type { BatchScoreResponse } from "@/features/batch-scoring/types";

export function runBatch(
  transactions: TransactionRequest[],
  batchId: string,
  signal: AbortSignal,
  token: string,
) {
  return apiRequest<BatchScoreResponse>("/batch-score", {
    method: "POST",
    token,
    signal,
    body: {
      batch_id: batchId || undefined,
      transactions,
    },
  });
}
