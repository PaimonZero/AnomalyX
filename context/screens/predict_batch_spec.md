# Predict Batch Screen Spec

## Purpose
The Predict Batch screen allows Compliance Officers and demo presenters to upload or paste a batch of transaction records, validate them against the system schema, run scoring through the AML engine, and review the resulting alert list — equivalent to UC-02 (Batch Scoring) in the PRD.

## Primary users
- Compliance Officer
- Admin
- Demo presenter

## Goals
- Accept a batch of `TransactionRequest` objects (CSV or JSON array)
- Validate against the canonical transaction schema before execution
- Execute `POST /api/v1/batch-score` and display results
- Allow row-level inspection of flagged records via the Batch Record Detail Modal
- Support export of results for compliance reporting

---

## Layout

### Split two-panel layout (desktop)
- **Left panel (40%)**: input + configuration + validation
- **Right panel (60%)**: preview → progress → results

On mobile: single-column stacked.

---

## Core components

### Left panel — Input

#### Input mode tabs
- **Upload file** — drag-and-drop zone accepting `.json` or `.csv`
- **Paste JSON** — textarea for a raw JSON array of transaction objects

#### Batch configuration form
| Field | Type | Note |
|-------|------|------|
| Batch name | Text input | Optional label for audit trail |
| Threshold override (τ_flag) | Number input (0.00–1.00) | Optional; defaults to system value `0.70` |
| Threshold override (τ_medium) | Number input (0.00–1.00) | Optional; defaults to system value `0.40` |
| Output format | Select | JSON · CSV |

#### Action buttons
- **Validate** — runs schema check without executing
- **Run Batch** — disabled until validation passes; calls `POST /api/v1/batch-score`
- **Reset** — clears all inputs and results
- **Cancel** — available while a job is in progress

### Left panel — Validation summary

Appears after validate/upload:
- ✓ Valid rows count
- ✗ Invalid rows count with expandable error list
- Per-error: row index, field name, error message

Blocks execution if any required field is missing or if `transaction_id` values are not unique within the batch.

### TransactionRequest schema reference (collapsible helper)

| Field | Type | Required | Note |
|-------|------|----------|------|
| `transaction_id` | string (UUID) | Yes | Idempotency key |
| `sender_id` | string (HMAC hash) | Yes | Pseudonymous identifier |
| `receiver_id` | string (HMAC hash) | Yes | Pseudonymous identifier |
| `sender_balance` | number | Yes | Balance before transaction (VND) |
| `receiver_balance` | number | Yes | Balance before transaction (VND) |
| `amount` | number ≥ 0 | Yes | Transaction amount |
| `currency` | string (ISO 4217) | Yes | Default: `VND` |
| `timestamp` | string (ISO-8601) | Yes | Event time with timezone |
| `channel` | enum | Yes | `PAYMENT` · `TRANSFER` · `CASH_OUT` · `CASH_IN` · `DEBIT` |
| `device_id` | string | No | Optional; for geo/device anomaly |
| `location_country` | string (ISO 3166-1 alpha-2) | No | Optional; e.g. `"VN"` |
| `location_region` | string | No | Optional; e.g. `"HN"` |

Note displayed in UI: "Optional geo/device fields are backward-compatible — omitting them is valid."

### Right panel — Progress (during execution)

- Progress bar (row-level: X of N processed)
- Live counter: Processed · Flagged · Failed
- Cancel button

### Right panel — Result summary cards (post-execution)

| Card | Value |
|------|-------|
| Total rows | Input count |
| Processed rows | Successfully scored |
| Flagged rows | `is_flagged = true` (HIGH + CRITICAL) |
| Failed rows | Rows that errored (with retry option) |
| Avg risk score | Mean `risk_score` across all processed |
| Decision breakdown | Donut chart: LOW / MEDIUM / HIGH / CRITICAL counts |

### Right panel — Results table

| Column | Field | Display |
|--------|-------|---------|
| # | Row index | — |
| Transaction ID | `transaction_id` | Mono, truncated |
| Sender | `sender_id` | Mono, truncated 8 chars |
| Amount | `amount` | Right-aligned, currency symbol |
| Channel | `channel` | Enum badge |
| Risk Score | `risk_score` | Decimal, tabular numerals |
| Risk Level | `risk_level` | Colored badge |
| Flagged | `is_flagged` | ✓ icon (HIGH/CRITICAL) or — |
| Triggered Rules | `triggered_rules[].id` | Mono chips |
| Actions | — | Open detail |

Filterable by `risk_level` and `is_flagged`. Default sort: `risk_score` descending.

### Export button
- Appears after completion
- Exports to JSON or CSV based on selected output format
- Filename: `anomalyx_batch_{batch_name}_{timestamp}.{ext}`

### Batch Record Detail Modal

Reuses Alert Detail Modal structure:
- Transaction summary (all input fields)
- `risk_score`, `risk_level`, `is_flagged`
- Triggered rules with severity badges
- SHAP top features with contribution bars
- Explanation text (or "Explanation pending…" if still generating)
- Manual flag action (same Escalate/Dismiss flow as Alerts page)

---

## API backing

| Action | Endpoint |
|--------|---------|
| Run batch | `POST /api/v1/batch-score` — body: `{ "transactions": [...TransactionRequest], "threshold_override": {...} }` |

Auth: `Authorization: Bearer <JWT_TOKEN>` required.

If batch processing is long-running (async job): poll a status endpoint. Show "Job submitted — processing…" with a polling spinner.

Response on completion: array of `PredictionResponse` objects, each matching the `/predict` response schema:
```json
{
  "transaction_id": "...",
  "risk_level": "HIGH",
  "is_flagged": true,
  "risk_score": 0.83,
  "triggered_rules": [{ "id": "R-STRUCT-01", "severity": "HIGH" }],
  "top_features": [
    { "name": "count_just_below_threshold_24h", "value": 4, "contribution": 0.31 }
  ],
  "explanation": null,
  "alert_id": "al_00921"
}
```

---

## States

### Empty (initial)
- Drag-and-drop empty state in the left panel: "Drop a JSON or CSV file here, or paste a JSON array below"
- Right panel: placeholder wireframe of the result table

### Validating
- Spinner in the validate button
- Validation summary populates incrementally

### Running
- Progress bar active; Run Batch button disabled and shows "Running…"
- Cancel button enabled

### Partial failure
- Failed row count card shown in red
- Expandable failed-rows list with error messages per row
- "Retry failed rows" button (re-submits only failed `transaction_id`s)

### Error
- If `POST /api/v1/batch-score` returns non-2xx: error banner "Batch failed — {error.code}: {error.message}" with retry
- Validation errors shown inline per row in the left panel

---

## Notes
- Schema validation must run client-side first before calling the API to surface malformed rows without a round-trip.
- The 400M VND CTR threshold is relevant context for structuring detection — the validation panel can note this to help users understand why amounts near that value are flagged.
- Optional `device_id` / `location_country` / `location_region` fields: show as optional in the schema helper; do not block validation if absent.
- Explanation generation is asynchronous — the batch result table may initially show `explanation = null`; a "Refresh explanations" polling button can update them.
