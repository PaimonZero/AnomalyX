# Alerts / Review Queue Screen Spec

## Purpose
The Alerts / Review Queue is the primary review workspace for suspicious transactions flagged by the AnomalyX Decision Engine. It enables Compliance Officers to inspect alerts, prioritize by risk, read LLM explanations, and take review actions (Escalate / Dismiss) — closing the operational loop and generating ground-truth labels for future model retraining.

## Primary users
- Compliance Officer (primary)
- Admin

## Goals
- List all `is_flagged = true` alerts in one filterable table
- Surface risk_level, risk_score, triggered rules, and explanation_source immediately
- Allow fast filtering and sorting by severity and recency
- Enable Escalate / Dismiss actions with mandatory confirmation (UI-02)
- Prevent accidental actions via confirmation dialog

---

## Layout

### Header area
- Page title "Alerts / Review Queue" + subtitle "Flagged transactions requiring review"
- Row: search input | status filter | risk level filter | typology filter | explanation source filter | date range picker | sort control | bulk action controls

### Main content
- Full-width alerts data table with sticky header
- Optional right-side detail drawer for quick preview (non-blocking)
- Pagination footer (default 25 per page; options: 10, 25, 50, 100)

---

## Core components

### Filter bar

| Filter | Type | Options |
|--------|------|---------|
| Search | Text input | Matches `alert_id` or `transaction_id` (partial) |
| Status | Multi-select | NEW · ESCALATED · DISMISSED |
| Risk level | Multi-select | CRITICAL · HIGH · MEDIUM · LOW |
| AML typology | Multi-select | structuring · smurfing · rapid_movement · layering · velocity_anomaly · geo_device_anomaly |
| Explanation source | Select | All · llm · template · pending |
| Date range | Date picker | `updated_at` range |
| Channel | Multi-select | PAYMENT · TRANSFER · CASH_OUT · CASH_IN · DEBIT |
| Sort | Select | Risk score desc · Updated at desc · Created at desc · Alert id asc |

### Alerts table columns

| Column | Field | Display rule |
|--------|-------|-------------|
| Alert ID | `alert_id` | Monospace, truncated 8 chars + copy icon |
| Transaction ID | `transaction_id` | Monospace, truncated 8 chars + copy icon |
| Risk Score | `risk_score` | Decimal (e.g. `0.83`), right-aligned, tabular numerals |
| Risk Level | `risk_level` | Colored badge: CRITICAL=red, HIGH=orange, MEDIUM=amber, LOW=green |
| Status | `status` | Badge: NEW=info, ESCALATED=red/critical, DISMISSED=muted |
| Triggered Rules | `triggered_rules[].id` | Comma-separated monospace rule IDs with severity chips |
| Explanation | `explanation_source` | `llm` badge (accent) or `template` badge (muted) or `pending…` pulsing |
| Updated | `updated_at` | Relative (e.g. "2h ago") with full ISO timestamp in tooltip |
| Actions | — | ⋯ menu: Open · Escalate · Dismiss |

Left border stripe per row colored by `risk_level` token.

### Alert Detail Modal (triggered from row click)

**Two-column layout (desktop): left = evidence, right = explanation + actions**

**Left column — Evidence:**
- Alert summary block: `alert_id`, `transaction_id`, `risk_score` (large), `risk_level` badge, `is_flagged` badge, model version
- Transaction context: `amount` (formatted VND), `currency`, `channel` badge, `timestamp`, `sender_id` (truncated), `receiver_id` (truncated)
- Triggered rules list: each rule as a card — `rule_id` (mono), `typology`, `severity` badge, `action_hint`
- SHAP top features list: each feature as a row — `name` (mono), `value`, contribution bar (visual) + numeric `contribution`
- Explanation source badge: `llm` or `template`

**Right column — Explanation + Actions:**
- Explanation panel: full natural-language text (bilingual Vietnamese/English)
  - If `explanation_source = llm`: show with `llm` badge
  - If `explanation_source = template`: show with `template` badge and a note "LLM unavailable — showing rule-based summary"
  - If explanation still generating: show "Explanation pending…" with pulse animation
- Reviewer note input (optional text area before action)
- Action buttons:
  - **Escalate** (orange/critical) — triggers confirmation dialog
  - **Dismiss** (muted) — triggers confirmation dialog
  - **Close** (ghost)
- Audit trail: `reviewer_id`, `updated_at`, `created_at`

**Escalate/Dismiss confirmation dialog:**
- Title: "Escalate this alert?" or "Dismiss this alert?"
- Body: brief consequence text ("This will flag the transaction as a confirmed AML case and create a ground-truth label for model retraining.")
- Reason select (required): pre-defined options per action type
- Note field (optional)
- Confirm + Cancel buttons (keyboard accessible, Escape = cancel)

On success: status updates inline in the table row; Toast: "Alert {alert_id} escalated" or "Alert {alert_id} dismissed".

### Bulk actions
- Checkbox column for multi-row selection
- Bulk action bar appears when ≥1 row selected: "N selected" | Bulk Escalate | Bulk Dismiss | Clear selection

---

## API backing

| Action | Endpoint |
|--------|---------|
| Load alerts list | `GET /api/v1/alerts?status=&risk_level=&page=&limit=` |
| Load alert detail | `GET /api/v1/alerts/{id}` |
| Escalate | `PATCH /api/v1/alerts/{id}/status` — body `{ "status": "ESCALATED", "reviewer_id": "...", "note": "..." }` |
| Dismiss | `PATCH /api/v1/alerts/{id}/status` — body `{ "status": "DISMISSED", "reviewer_id": "...", "note": "..." }` |

Auth: `Authorization: Bearer <JWT_TOKEN>` required on all alert endpoints.

Error handling: if PATCH fails (DB connection lost per PRD §4.1.4 abnormal case), show error toast "Action failed — please retry" and retain the previous status. Do not optimistically update the row.

---

## States

### Loading
- Skeleton rows (8 rows) while `GET /api/v1/alerts` is in flight
- Skeleton in the detail modal while `GET /api/v1/alerts/{id}` loads

### Empty
- "No alerts match your current filters" with a "Clear filters" link
- If truly no alerts exist: "No flagged transactions yet — run Predict Batch or test via API Testing"

### Error
- Retryable error banner if the alert list cannot load: "Failed to load alerts — {error.code}: {error.message}" with Retry button
- Inline per-row error if a single action fails

---

## Notes
- Only `is_flagged = true` alerts appear here (HIGH + CRITICAL). MEDIUM risk_level transactions are log-only and visible in Audit Log, not this queue.
- `explanation_source` must always be displayed — never show explanation text without indicating whether it came from LLM or a fallback template (EXP-01).
- Sender/receiver IDs: display truncated (first 8 chars + "…"); full value available via copy icon only (SEC-01, PII hygiene).
- Actions (Escalate, Dismiss) always require a confirmation dialog before the PATCH is sent (UI-02).
- The status change creates a ground-truth label used by ML/Risk Engineer for model retraining (UC-04).
