# Dashboard Screen Spec

## Purpose
The Dashboard is the main landing page of the AnomalyX Admin Console. It provides a system-wide operational overview for Admin, Compliance Officer, and ML/Risk Engineer users — covering system health, alert status, Prometheus metrics, and quick navigation into all core workflows.

## Primary users
- Compliance Officer (default landing view)
- ML/Risk Engineer (secondary monitoring entry point)
- Demo Evaluator/Mentor

## Goals
- Summarize current service health from `GET /health` (model loaded, rules loaded, DB reachable)
- Show high-level Prometheus metrics from `GET /metrics`
- Surface the latest flagged alerts (HIGH + CRITICAL) immediately
- Show recent batch jobs and API tests as activity context
- Provide quick navigation into every major workflow

---

## Layout

### App shell
- Fixed sidebar on the left (240px)
- Top header bar: page title "Dashboard", environment badge (Local / Dev / Demo), theme toggle, global search, notifications, user menu
- Main content area: responsive grid

### Main page structure (top → bottom)
1. **KPI summary row** — 6 metric cards across the full width
2. **Prometheus charts row** — 4 charts in a 2×2 grid
3. **Service health + Decision distribution row** — health status cards left, decision donut/bar right
4. **Recent activity row** — recent alerts table + recent batch jobs list side by side
5. **Quick actions panel** — compact bottom or right panel

---

## Core components

### KPI cards (6 cards, top row)
Each card shows: current value, delta vs prior period, a trend sparkline, and a status badge.

| Card | Metric source | Threshold / note |
|------|--------------|-----------------|
| Total Predictions | `request_count` (Prometheus) | All time or time-windowed |
| Flagged Alerts | Count of alerts where `is_flagged = true` | HIGH + CRITICAL only |
| HIGH / CRITICAL Alerts | Count by `risk_level` | Color: `--risk-high` / `--risk-critical` |
| Avg p95 Latency | `request_latency` p95 from Prometheus | Target ≤ 500 ms |
| Explanation Success Rate | `1 - (llm_fallback_total / decisions_total)` | Source: `explanation_source` distribution |
| Rule Hit Rate | `rule_trigger_total` across all rules | Fraction of predictions that triggered ≥1 rule |

### Prometheus charts (2×2 grid)

| Chart | Metric | Type |
|-------|--------|------|
| Requests over time | `request_count` (rate) | Area/line chart |
| p95 Latency trend | `request_latency` histogram p95 | Line chart; threshold line at 500 ms |
| Decision distribution | `decisions_total{decision}` — LOW / MEDIUM / HIGH / CRITICAL | Stacked bar or donut |
| Rule trigger trend | `rule_trigger_total{rule_id}` — per rule (R-STRUCT-01, R-SMURF-01, R-RAPID-01, R-LAYER-01, R-VELO-01, R-GEO-01) | Grouped bar |

### Service health cards

Status chips sourced from `GET /health`. Each card shows: component name, status (UP / DOWN / DEGRADED), and latency/version info where available.

| Component | Health check detail |
|-----------|-------------------|
| API service | Liveness / readiness from `/health` |
| ML model loaded | `model_version` from model registry |
| Rule engine loaded | Active rule count + `rule_version` |
| PostgreSQL | DB reachability |
| Redis | Cache/aggregate store reachability |
| LLM provider | Last successful call timestamp (async path only) |

### Recent alerts table (compact, last 10)

Columns: `alert_id` (mono), `transaction_id` (mono, truncated 8 chars), `risk_score` (decimal), `risk_level` badge, `status` badge, `triggered_rules` (comma-separated rule ids), `updated_at` (relative).

Only shows `is_flagged = true` rows (HIGH + CRITICAL).
Left border stripe colored by `risk_level`.

### Recent batch jobs list (compact, last 5)

Fields: batch name, start time, total rows, flagged count, status (running / completed / failed).

### Recent API tests list (compact, last 5)

Fields: endpoint called, method, status code, latency, timestamp.

### Quick actions panel

| Button | Action |
|--------|--------|
| Open Alerts | Navigate to Alerts / Review Queue |
| Run Batch | Navigate to Predict Batch |
| Test API | Navigate to API Testing |
| Manage Rules | Navigate to Rule Engine |
| View Monitoring | Navigate to Model & Metrics Monitor |

---

## Decision Logic Reference (informational widget)

A small collapsible reference card showing the Decision Matrix from TDD §1.4.3:

| Rule output | ML risk_score | risk_level | is_flagged |
|-------------|--------------|-----------|-----------|
| CRITICAL rule | Any | CRITICAL | true |
| HIGH rule | Any | HIGH | true |
| None / MINOR | ≥ 0.70 | HIGH | true |
| MINOR rule | 0.40–0.69 | MEDIUM | false |
| None | 0.40–0.69 | MEDIUM | false |
| None / MINOR | < 0.40 | LOW | false |

Thresholds: τ_medium = 0.40, τ_flag = 0.70 (configurable via Settings).

---

## Interaction model
- Clicking an alert row opens the Alert Detail Modal
- Clicking a batch row navigates to Predict Batch with that job loaded
- Clicking a chart card navigates to Model & Metrics Monitor
- Clicking a health card that is DOWN shows an error detail tooltip
- Quick actions are primary shortcuts for demo flow

---

## States

### Loading
- Skeleton cards for all KPI cards and charts
- Skeleton rows for alert and job tables

### Empty
- Welcoming empty state: "No predictions yet — start with API Testing or Predict Batch"
- Single CTA button to open API Testing

### Error
- Compact error banner if `/metrics` or `/health` fails; show "Metrics unavailable — retry" with a refresh button
- Keep the rest of the dashboard visible if partial data loads
- Per-widget error state if individual widget fails

---

## Notes
- `is_flagged = true` only for HIGH and CRITICAL alerts. MEDIUM (risk_score 0.40–0.70) is log-only and should not appear in the alert table unless specifically filtered.
- All IDs displayed in monospace; truncate sender/receiver IDs to first 8 characters.
- Do not mix decimal and percentage formats for `risk_score` on the same screen — use decimal (e.g. `0.83`) in tables and percentage (e.g. `83%`) in KPI cards.
- `explanation_source` should be shown as an `llm` or `template` badge. If explanation is still pending (async), show "Explanation pending…" with a pulse indicator.
