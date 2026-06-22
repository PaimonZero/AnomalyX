# Model & Metrics Monitor Screen Spec

## Purpose
The Model & Metrics Monitor provides the primary observability page for the AnomalyX system — covering Prometheus-scraped API metrics, ML model health, rule trigger rates, drift indicators, and LLM explanation quality — fulfilling UC-06 (Monitor Model & Metrics) from the PRD.

## Primary users
- ML/Risk Engineer (primary)
- Admin

## Goals
- Monitor real-time service health from `GET /api/v1/health` and `GET /api/v1/metrics`
- Visualize all locked Prometheus metrics from TDD §8
- Display the locked success metric targets alongside current values so the engineer can see at-a-glance whether the system is meeting them
- Surface model and rule performance indicators
- Show drift gauge (PSI) and explanation quality / fallback rates
- Allow time-range selection and manual refresh

---

## Layout

1. **Top summary row** — health status chips + critical KPI badges
2. **Metric target compliance row** — shows locked thresholds vs current values
3. **Chart grid (2×3)** — 6 core Prometheus charts
4. **Model card + feature importance row** — model metadata + SHAP global importance chart
5. **Drift + explanation quality row** — PSI gauge, score distribution, LLM quality cards

---

## Core components

### Health status chips (top row, always visible)

Sourced from `GET /api/v1/health`. Display as compact horizontal chips with colored indicators:

| Component | Status source |
|-----------|--------------|
| API service | liveness check |
| ML model | `model_version` + loaded state |
| Rule engine | active rules count + `rule_version` |
| PostgreSQL | DB reachability |
| Redis | Cache + rolling aggregate store |
| LLM provider | Last successful explanation timestamp |

Each chip: component name + status dot (green UP / red DOWN / amber DEGRADED).

### Metric target compliance cards

Display the locked metrics from TDD §10 with current measured values and a pass/fail badge:

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Precision (suspicious class) | ≥ 0.70 | {value} | ✓ / ✗ |
| Recall (suspicious class) | ≥ 0.60 | {value} | ✓ / ✗ |
| F1 score | ≥ 0.65 | {value} | ✓ / ✗ |
| PR-AUC | ≥ 0.50 | {value} | ✓ / ✗ |
| AUC-ROC | ≥ 0.85 | {value} | ✓ / ✗ |
| Model false-positive rate | ≤ 5% | {value} | ✓ / ✗ |
| Rule false-positive rate | ≤ 8% | {value} | ✓ / ✗ |
| p95 latency (excl. LLM) | ≤ 500 ms | {value} | ✓ / ✗ |
| p95 latency (incl. LLM async) | ≤ 3 s | {value} | ✓ / ✗ |
| Throughput | ≥ 50 req/s | {value} | ✓ / ✗ |

Source: a combination of ML evaluation reports stored at model registration time and live Prometheus data.

### Chart grid (6 charts)

All charts support time-range selector: Last 1h · Last 6h · Last 24h · Last 7d

| Chart | Prometheus metric | Chart type |
|-------|------------------|-----------|
| Request volume | `request_count` (rate per minute) | Area chart |
| p50 / p95 / p99 Latency | `request_latency` histogram buckets | Multi-line; threshold line at 500 ms |
| Alert rate | `decisions_total{decision="HIGH"} + decisions_total{decision="CRITICAL"}` / total | Line chart |
| Decision distribution | `decisions_total{decision}` — LOW / MEDIUM / HIGH / CRITICAL | Stacked bar (time series) |
| Rule trigger counts | `rule_trigger_total{rule_id}` — one series per rule ID | Grouped bar |
| Score distribution | `score_histogram` | Histogram chart; vertical lines at τ_medium=0.40 and τ_flag=0.70 |

### Model card

Compact panel showing the registered model metadata:

| Field | Value |
|-------|-------|
| Model version | `model_version` (e.g. `mock-ml-v1`) |
| Algorithm | XGBoost / LightGBM (from registry) |
| Training data | PaySim dataset, hash fingerprint |
| Training date | ISO timestamp |
| τ_medium threshold | `0.40` (configurable) |
| τ_flag threshold | `0.70` (configurable) |
| Feature count | N features |
| Calibration method | Platt / isotonic |

### SHAP global feature importance chart

Horizontal bar chart of top-10 features by mean absolute SHAP value:
- Features ordered by importance descending
- Each bar labeled with feature name (mono font) and importance value
- Grouped by feature group: Transaction / Velocity / Counterparty / Behavioural / Sequence / Structuring (color-coded)

### Drift & quality section

#### Drift gauge (PSI)
- Population Stability Index card for score distribution
- Current PSI value + threshold (e.g. PSI > 0.20 = significant drift)
- Status: STABLE / MODERATE / SIGNIFICANT with color coding
- Trend sparkline

#### Score distribution comparison
- Overlay chart: training distribution vs. recent inference distribution
- Visual indication of shift (KS test statistic if available)

#### LLM explanation quality cards

| Card | Metric | Source |
|------|--------|--------|
| Explanation success rate | `1 - llm_fallback_total / decisions_total` (for flagged) | Prometheus |
| LLM fallback rate | `llm_fallback_total` per hour | Prometheus |
| LLM avg latency | `llm_latency` p95 | Prometheus |
| Groundedness pass rate | From qualitative review results (manual) | Static from W5 review |
| Last successful LLM call | Timestamp | Health check |

---

## Interaction model
- **Refresh** button in the header: forces a new scrape of `/api/v1/metrics`
- **Auto-refresh toggle**: refresh every 30s (off by default)
- **Time range selector**: applies to all charts simultaneously
- Clicking a chart opens a modal with a larger, more detailed view of that chart
- Clicking a metric target card shows the measurement methodology as a tooltip

---

## States

### Loading
- Skeleton cards and chart placeholders with shimmer animation

### Empty
- When no metric window is available yet: "No metric data available — start running predictions to populate this page"
- Charts show an empty state illustration

### Error
- If `/api/v1/metrics` scrape fails: "Metrics unavailable — Prometheus may not be running. Retry?" banner
- Individual chart error: "Chart data unavailable" placeholder with retry icon
- Health chip turns red immediately on component failure

### Abnormal (high resource utilization per PRD §4.1.6)
- If CPU/RAM exceeds threshold: alert banner at the top of the page: "⚠ High system load detected — metric updates may be delayed. Prediction API remains operational."

---

## Notes
- The Score Distribution chart should draw vertical threshold lines at τ_medium=0.40 and τ_flag=0.70 to make the decision boundaries visually clear.
- Prometheus metric names (exact, from TDD §8):
  - `request_count` — counter
  - `request_latency` — histogram (p50/p95/p99)
  - `decisions_total{decision}` — counter per decision level
  - `rule_trigger_total{rule_id}` — counter per rule
  - `llm_latency` — histogram
  - `llm_fallback_total` — counter
  - PSI drift gauge (custom)
- The model metrics (Precision, Recall, F1, AUC-ROC, PR-AUC) come from the model registry at training time — they are not computed live. Display them clearly alongside service-level metrics to avoid confusion.
- This page can stay lean and technical. Lightweight health previews are mirrored on the Dashboard; deep observability lives here.
