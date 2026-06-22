import type { BatchValidationError, BatchValidationResult } from "@/features/batch-scoring/types";
import type { TransactionChannel, TransactionRequest } from "@/shared/types/api";

const channels: TransactionChannel[] = ["PAYMENT", "TRANSFER", "CASH_OUT", "CASH_IN", "DEBIT"];
const requiredFields = [
  "transaction_id",
  "sender_id",
  "receiver_id",
  "sender_balance",
  "receiver_balance",
  "amount",
  "currency",
  "timestamp",
  "channel",
] as const;

export function validateBatchJson(raw: string): BatchValidationResult {
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return { transactions: [], errors: [{ index: 0, field: "json", message: "Content is not valid JSON." }] };
  }

  if (!Array.isArray(parsed)) {
    return { transactions: [], errors: [{ index: 0, field: "root", message: "Data must be a JSON array." }] };
  }

  const transactions: TransactionRequest[] = [];
  const errors: BatchValidationError[] = [];
  const seenIds = new Set<string>();

  parsed.forEach((value, index) => {
    if (typeof value !== "object" || value === null) {
      errors.push({ index, field: "row", message: "Each row must be an object." });
      return;
    }

    const row = value as Record<string, unknown>;
    const rowErrors: BatchValidationError[] = [];
    requiredFields.forEach((field) => {
      if (row[field] === undefined || row[field] === null || row[field] === "") {
        rowErrors.push({ index, transactionId: String(row.transaction_id ?? ""), field, message: "Required field is missing." });
      }
    });

    if (typeof row.amount !== "number" || row.amount < 0) {
      rowErrors.push({ index, transactionId: String(row.transaction_id ?? ""), field: "amount", message: "Amount must be a number greater than or equal to 0." });
    }
    if (typeof row.currency !== "string" || row.currency.length !== 3) {
      rowErrors.push({ index, transactionId: String(row.transaction_id ?? ""), field: "currency", message: "Currency must be exactly 3 characters." });
    }
    if (!channels.includes(row.channel as TransactionChannel)) {
      rowErrors.push({ index, transactionId: String(row.transaction_id ?? ""), field: "channel", message: "Channel is not supported." });
    }
    if (typeof row.timestamp !== "string" || Number.isNaN(Date.parse(row.timestamp))) {
      rowErrors.push({ index, transactionId: String(row.transaction_id ?? ""), field: "timestamp", message: "Timestamp must be a valid ISO-8601 value." });
    }

    const transactionId = String(row.transaction_id ?? "");
    if (transactionId && seenIds.has(transactionId)) {
      rowErrors.push({ index, transactionId, field: "transaction_id", message: "Transaction ID is duplicated in the batch." });
    }
    if (transactionId) seenIds.add(transactionId);

    if (rowErrors.length) errors.push(...rowErrors);
    else transactions.push(row as unknown as TransactionRequest);
  });

  return { transactions, errors };
}
