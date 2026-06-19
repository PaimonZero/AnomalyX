import assert from "node:assert/strict";
import test from "node:test";

import { validateBatchJson } from "./batch-validation.ts";

const validTransaction = {
  transaction_id: "tx_001",
  sender_id: "sender_001",
  receiver_id: "receiver_001",
  sender_balance: 1_000_000,
  receiver_balance: 500_000,
  amount: 120_000,
  currency: "VND",
  timestamp: "2026-06-19T09:12:04+07:00",
  channel: "TRANSFER",
};

test("validateBatchJson accepts valid transaction arrays for automatic batch checks", () => {
  const result = validateBatchJson(JSON.stringify([validTransaction], null, 2));

  assert.equal(result.errors.length, 0);
  assert.equal(result.transactions.length, 1);
  assert.equal(result.transactions[0].transaction_id, "tx_001");
});

test("validateBatchJson reports invalid JSON for automatic batch checks", () => {
  const result = validateBatchJson("[");

  assert.equal(result.transactions.length, 0);
  assert.equal(result.errors.length, 1);
  assert.equal(result.errors[0].field, "json");
});
