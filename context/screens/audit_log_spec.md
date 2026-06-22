# Audit Log Screen Spec

## Purpose
The Audit Log provides a traceable history of all key system and user actions — predictions, manual review decisions, rule changes, rule reloads, and batch job completions — supporting AML compliance requirements and operational debugging. This implements the audit trail requirement from PRD §5.2.3 (SEC-01) and TDD §8 (structured JSON logging).

## Primary users
- Admin (primary)
- Compliance Officer (review trail, STR preparation)
- ML/Risk Engineer (debugging, rule change history)

## Goals
- Record every operational event with structured fields
- Support traceability for AML review workflows (alert → decision → ground-truth label chain)
- Allow filtering and inspection of activity history by actor, action type, and date range
- Export audit records for compliance reports
- Show that PII hygiene is maintained: only hashed IDs and prediction results are logged, never raw transaction payloads (SEC-01)

---

## Layout

### Top filter bar
- Search input + action type filter + actor role filter + date range filter + export button

### Main content
- Activity table (primary view) — dense, timestamped, one row per event
- Optional event detail drawer (side panel when row clicked)

---

## Core components

### Filter bar

| Filter | Type | Options |
|--------|------|---------|
| Search | Text | Matches `transaction_id`, `alert_id`, `rule_id`, `actor_id` |
| Action type | Multi-select | See event categories below |
| Actor role | Multi-select | compliance_officer · ml_engineer · admin · system |
| Date range | Date range picker | Applied to `timestamp` |
| Decision | Multi-select | LOW · MEDIUM · HIGH · CRITICAL (for prediction events) |
| Export | Button | Download filtered set as JSON or CSV |

### Audit records table

| Column | Field | Display |
|--------|-------|---------|
| Timestamp | `timestamp` | `yyyy-MM-dd HH:mm:ss` (mono), relative tooltip |
| Event type | `action_type` | Colored chip (see event categories) |
| Actor | `actor_id` + `actor_role` | Role badge + ID (mono, truncated) |
| Entity | `entity_type` + `entity_id` | e.g. Alert `al_00921` or Rule `R-STRUCT-01` (mono) |
| Description | `description` | Short human-readable summary |
| Decision / Result | `decision` or `status` | Risk level badge or status badge where applicable |
| Latency | `latency_ms` | Tabular numerals (ms), shown only for prediction events |

### Event categories (action_type values)

| Action type | Triggered by | Display color |
|------------|-------------|--------------|
| `prediction` | POST /api/v1/predict | Accent (info) |
| `batch_job` | POST /api/v1/batch-score | Accent secondary |
| `alert_escalated` | PATCH /api/v1/alerts/{id}/status (ESCALATED) | Risk high/critical |
| `alert_dismissed` | PATCH /api/v1/alerts/{id}/status (DISMISSED) | Muted/success |
| `manual_flag` | Manual flag action from UI | Risk medium |
| `rule_created` | Rule form save | Secondary accent |
| `rule_updated` | Rule form save | Secondary accent |
| `rule_deleted` | Rule delete + confirmation | Warning |
| `rule_reloaded` | POST /api/v1/rules/reload | Success |
| `rule_reload_failed` | POST /api/v1/rules/reload (error) | Error |
| `api_test` | API Testing screen — Send request | Muted info |
| `llm_explanation_generated` | Background LLM task completion | Muted accent |
| `llm_explanation_fallback` | LLM timeout/error → template fallback | Warning |

### Structured log fields displayed per event (from TDD §8)

For `prediction` events:
- `request_id`, `transaction_id`, `decision` (risk_level), `latency_ms`, `model_version`, `rule_version`
- IDs are hashed — display as monospace truncated with tooltip noting "hashed identifier (SEC-01)"
- `triggered_rules` list (if any)

For `alert_escalated` / `alert_dismissed` events:
- `alert_id`, `transaction_id`, `reviewer_id`, `new_status`, `note`, `timestamp`

For `rule_reloaded` / `rule_reload_failed` events:
- `rule_version`, `rules_count`, `error_message` (on failure), `triggered_by`

For `batch_job` events:
- Batch name, total rows, flagged rows, failed rows, duration_ms

### Event detail drawer

Opens on row click; shows all fields for that event in a key-value list format:
- Full `request_id` in monospace
- Full structured log payload (non-PII fields only)
- Related entity link (e.g., "Open Alert al_00921" → navigates to Alerts page)
- Raw JSON toggle (expandable)

---

## Export

- Exports filtered audit records as JSON (structured log format) or CSV
- Filename: `anomalyx_audit_{date_range}.{ext}`
- Exported fields match the table columns plus full `request_id`
- Note in UI: "Exported records contain hashed identifiers only — no raw PII"

---

## States

### Loading
- Skeleton rows (10 rows) while fetch is in flight

### Empty
- If no audit records exist yet: "Audit trail is empty — actions will appear here once the system processes transactions"
- If filters return no results: "No events match your current filters" + Clear filters link

### Error
- Retryable banner if log retrieval fails: "Failed to load audit log — {error.code}: {error.message}" + Retry button

---

## Notes
- **PII hygiene is a visible feature here**: display a small notice at the top of the page — "All identifiers are hashed (HMAC-SHA256). Raw PII is never stored (SEC-01)." This reinforces compliance to the Mentor/Evaluator.
- The `prediction` events for MEDIUM risk transactions (log-only, `is_flagged = false`) appear here but NOT in the Alerts / Review Queue. This is the only place to see the full decision trail for non-flagged transactions.
- The audit log is append-only — no delete or edit actions are exposed in this UI.
- For the demo: the log should show a clear narrative — POST predict → alert created → alert escalated — as a connected chain. Use the `entity_id` links to make this chain navigable.
- Pagination: default 50 rows per page, with options 25 / 50 / 100.
