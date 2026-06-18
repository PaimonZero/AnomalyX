# AnomalyX Admin Console — Sitemap & Screen Specs

## 1. Purpose

This document defines the frontend information architecture and screen-level UI specifications for the AnomalyX Admin Console. The goal is a data-centric, minimalist, operations-first interface for compliance review, API testing, batch scoring, rule management, observability, and audit.

The stack is **React + Vite + TypeScript + Tailwind CSS + shadcn/ui**.

---

## 2. Product UI Principles

- **Operations-first**, not marketing-oriented — every screen serves a workflow, not a narrative.
- **Single sidebar-based app shell** for fast navigation between sections.
- **Dense but readable**: compact tables, tight charts, clear action placement.
- **Cards for summaries**, **tables for investigation**, **drawers/modals for detail and editing**.
- **Decision surface**: the Alert Detail modal is not just an information panel — it is where the Compliance Officer makes a reviewable decision.
- Keep small supporting widgets inside the **Dashboard** rather than splitting them into standalone pages.

---

## 3. Sitemap

```text
AnomalyX Admin Console
├─ Dashboard
│  ├─ KPI summary row (6 cards)
│  ├─ Prometheus charts (4 charts)
│  ├─ Service health status (6 components)
│  ├─ Decision distribution widget
│  ├─ Recent alerts table (is_flagged=true only)
│  ├─ Recent batch jobs list
│  ├─ Recent API tests list
│  └─ Quick actions panel
│
├─ Alerts / Review Queue
│  ├─ Filter bar (status, risk_level, typology, channel, date range)
│  ├─ Alerts table (is_flagged=true, HIGH + CRITICAL)
│  ├─ Alert Detail Modal
│  │  ├─ Evidence column (risk summary, triggered rules, SHAP features)
│  │  ├─ Explanation column (LLM/template text, source badge)
│  │  └─ Action buttons (Escalate / Dismiss + confirmation dialog)
│  └─ Bulk actions (Escalate / Dismiss / Mark reviewed)
│
├─ Predict Batch
│  ├─ Input panel (upload / paste JSON)
│  ├─ TransactionRequest schema reference
│  ├─ Batch configuration (thresholds, output format)
│  ├─ Schema validation preview
│  ├─ Batch run progress
│  ├─ Result summary cards
│  ├─ Batch results table
│  └─ Batch Record Detail Modal
│
├─ API Testing (Demo)
│  ├─ Endpoint picker (9 endpoints)
│  ├─ Request builder (method, auth, headers, params, body)
│  ├─ Example payload presets (per endpoint)
│  ├─ Response viewer (status, latency, JSON body)
│  ├─ Error envelope display
│  ├─ Request history
│  └─ Saved sample presets
│
├─ Rule Engine
│  ├─ Rules table (6+ rules)
│  ├─ Rule detail / edit drawer
│  │  ├─ YAML-aware form (id, typology, severity, condition DSL, window, action_hint)
│  │  ├─ DSL feature name helper
│  │  ├─ YAML preview tab
│  │  ├─ Rule test panel (evaluate against sample context)
│  │  └─ Version history panel
│  └─ Reload Rules flow (confirm → POST /api/v1/rules/reload → banner)
│
├─ Model & Metrics Monitor
│  ├─ Health status chips (6 components)
│  ├─ Locked metric compliance cards (11 targets vs current)
│  ├─ Prometheus charts (6 charts with time-range selector)
│  ├─ Model card (version, algorithm, thresholds, feature count)
│  ├─ SHAP global feature importance chart
│  ├─ Drift gauge (PSI)
│  └─ LLM explanation quality cards
│
├─ Audit Log
│  ├─ Filter bar (action type, actor role, decision, date range)
│  ├─ Activity table (all event categories)
│  ├─ Event detail drawer
│  └─ Export (JSON / CSV)
│
└─ Settings
   ├─ Environment status card
   ├─ Auth & API token card (masked, copy-only)
   ├─ Decision thresholds (τ_medium=0.40, τ_flag=0.70)
   ├─ Regulatory constants (CTR=400M VND — read-only)
   ├─ LLM provider config
   ├─ Feature flags
   └─ Provider / repository status
```

---

## 4. Page Allocation

### Standalone pages
Each carries enough workflow depth, state, or recurrence:
- Dashboard
- Alerts / Review Queue
- Predict Batch
- API Testing
- Rule Engine
- Model & Metrics Monitor
- Audit Log
- Settings

### Modal / drawer overlays (not separate pages)
- Alert Detail Modal — triggered from Dashboard, Alerts, Predict Batch
- Batch Record Detail Modal — triggered from Predict Batch results
- Rule Detail / Edit Drawer — triggered from Rule Engine table
- Event Detail Drawer — triggered from Audit Log table

---

## 5. Shared UI Primitives (shadcn/ui)

Do not hand-roll these — use shadcn components:

`Button` · `Card` · `CardHeader` · `CardContent` · `Badge` · `Tabs` · `TabsList` · `TabsTrigger` · `TabsContent` · `Dialog` · `AlertDialog` · `Sheet` · `Drawer` · `DropdownMenu` · `Input` · `Textarea` · `Select` · `Switch` · `Separator` · `Table` · `TableHeader` · `TableRow` · `TableCell` · `Progress` · `Skeleton` · `Tooltip` · `ScrollArea` · `Toast`

---

## 6. Global Layout

### Sidebar (fixed, 240px)
- Brand / logo area at top: "AnomalyX" wordmark + AML badge
- Section groups:
  - **Operations**: Dashboard · Alerts · Predict Batch
  - **Engineering**: API Testing · Rule Engine · Model & Metrics Monitor
  - **Governance**: Audit Log · Settings
- Active item: accent-primary left border + subtle bg highlight

### Header (56px, fixed)
- Left: page title (`text-xl font-semibold`) + subtitle (`text-sm text-muted`)
- Right: environment badge (`LOCAL`/`DEV`/`DEMO`) + global search + notifications icon + theme toggle (sun/moon) + user menu

### Content area
- Scrollable, responsive grid
- Default padding: `p-6` on desktop, `p-4` on mobile
- Max content width: `max-w-screen-2xl`

---

## 7. AML Domain Data Reference

Shared across all screens — exact types from TDD.

### Transaction fields (TransactionRequest)

| Field | Type | Values / format |
|-------|------|----------------|
| `transaction_id` | string UUID | Idempotency key |
| `sender_id` | string (HMAC hash) | Display: first 8 chars + "…" |
| `receiver_id` | string (HMAC hash) | Display: first 8 chars + "…" |
| `sender_balance` | number | VND amount |
| `receiver_balance` | number | VND amount |
| `amount` | number ≥ 0 | VND amount |
| `currency` | string ISO 4217 | Default `VND` |
| `timestamp` | string ISO-8601 | With timezone offset |
| `channel` | enum | `PAYMENT` · `TRANSFER` · `CASH_OUT` · `CASH_IN` · `DEBIT` |
| `device_id` | string (optional) | Device/hardware identifier |
| `location_country` | string ISO 3166-1 (optional) | e.g. `VN` |
| `location_region` | string (optional) | e.g. `HN` |

### Alert fields

| Field | Type | Values |
|-------|------|--------|
| `alert_id` | string | Primary key |
| `transaction_id` | string | Reference |
| `risk_score` | float [0,1] | Calibrated ML probability |
| `risk_level` | enum | `LOW` · `MEDIUM` · `HIGH` · `CRITICAL` |
| `is_flagged` | boolean | true only for HIGH + CRITICAL |
| `triggered_rules` | array | `{ id, severity }` per rule |
| `top_features` | array | `{ name, value, contribution }` — SHAP top-k |
| `explanation` | string or null | Natural language (async, may be null) |
| `explanation_source` | enum | `llm` · `template` |
| `status` | enum | `NEW` · `ESCALATED` · `DISMISSED` |
| `reviewer_id` | string | ID of reviewer |
| `updated_at` | timestamp | Audit timestamp |

### Decision thresholds (configurable, locked defaults from TDD §10)

| Threshold | Default | Effect |
|-----------|---------|--------|
| τ_medium | 0.40 | `risk_score >= 0.40` → MEDIUM (log-only) |
| τ_flag | 0.70 | `risk_score >= 0.70` → HIGH + `is_flagged = true` |
| CTR threshold | 400,000,000 VND | Legal constant (Decision 11/2023/QĐ-TTg) |

### AML rule IDs and typologies

| Rule ID | Typology | Severity |
|---------|----------|----------|
| `R-STRUCT-01` | structuring | HIGH |
| `R-SMURF-01` | smurfing | HIGH |
| `R-RAPID-01` | rapid_movement | HIGH |
| `R-LAYER-01` | layering | MEDIUM |
| `R-VELO-01` | velocity_anomaly | MEDIUM |
| `R-GEO-01` | geo_device_anomaly | MEDIUM |

---

## 8. API Surface Reference

| Method + path | Auth | Used by screen |
|---------------|------|---------------|
| `GET /health` | None | Dashboard, Monitor |
| `GET /metrics` | None | Dashboard, Monitor |
| `POST /api/v1/predict` | JWT | API Testing |
| `POST /api/v1/batch-score` | JWT | Predict Batch |
| `GET /api/v1/alerts` | JWT | Dashboard, Alerts |
| `GET /api/v1/alerts/{id}` | JWT | Alert Detail Modal |
| `PATCH /api/v1/alerts/{id}/status` | JWT | Alert Detail Modal |
| `GET /api/v1/rules` | JWT | Rule Engine, Settings |
| `POST /api/v1/rules/reload` | JWT | Rule Engine |

Error envelope (all protected endpoints):
```json
{ "error": { "code": "...", "message": "...", "details": {...} } }
```

---

## 9. Recommended Frontend Structure

```text
src/
├─ app/
│  ├─ routes/
│  ├─ layout/         ← AppShell, Sidebar, Header
│  └─ providers/      ← ThemeProvider, QueryClientProvider, AuthProvider
├─ components/
│  ├─ ui/             ← shadcn primitives (do not edit)
│  ├─ common/         ← shared: RiskBadge, ExplanationSourceBadge, IDCell
│  ├─ charts/         ← Recharts/Nivo wrappers
│  └─ data-table/     ← Generic sortable/filterable table
├─ features/
│  ├─ dashboard/
│  ├─ alerts/
│  ├─ batch/
│  ├─ api-testing/
│  ├─ rules/
│  ├─ monitoring/
│  ├─ audit/
│  └─ settings/
├─ lib/
│  ├─ api.ts          ← Typed fetch wrappers for all 9 endpoints
│  └─ constants.ts    ← τ_medium, τ_flag, CTR_THRESHOLD, CHANNEL_VALUES, RULE_IDS
├─ hooks/
├─ types/
│  ├─ transaction.ts  ← TransactionRequest type
│  ├─ alert.ts        ← Alert, RiskLevel, AlertStatus, ExplanationSource
│  └─ rule.ts         ← Rule, Typology, Severity, ActionHint
└─ styles/
   └─ globals.css     ← CSS custom properties for both themes
```

---

## 10. Summary

The admin console ships as a single-page application with a shared sidebar layout. The 8 standalone pages each map to a distinct use case from the PRD. Modals and drawers handle detail and editing without losing table context. Domain-specific data types (risk levels, rule IDs, alert statuses, AML typologies) are treated as first-class design tokens — colored, labeled, and monospace-formatted consistently across every screen.
