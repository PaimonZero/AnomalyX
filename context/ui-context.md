# UI Context

## Current Product Surface

Current implementation is backend-only. No React/Vite frontend exists in source yet. This file defines future dashboard conventions from PRD/TDD so frontend work can start consistently, but backend changes must not assume UI files exist.

## Target Users

- **Compliance Officer** — primary dashboard user; needs alert triage, clear risk evidence, and safe review actions.
- **ML/Risk Engineer** — secondary admin/operator; needs active rule visibility, reload feedback, health, and metrics.
- **Demo Evaluator/Mentor** — needs clean end-to-end prototype demo through API and eventual dashboard.

## Target Screens

### Dashboard Overview

- Alert count by status.
- HIGH/CRITICAL count and rate.
- Recent flagged transactions.
- Basic system health indicators from `/api/v1/health` and `/api/v1/metrics`.

### Alert List

- Table of alerts from `GET /api/v1/alerts`.
- Columns: alert id, transaction id, risk level, risk score, status, created time, explanation source.
- Filters: status, risk level, date range when backend supports them.
- Row click opens alert detail.

### Alert Detail

- Risk summary: `risk_level`, `risk_score`, `is_flagged`, `model_version`.
- Rule evidence: triggered rules with id, severity, typology.
- Feature evidence: top features with name, value, contribution.
- Explanation panel: LLM/template explanation and source badge.
- Review controls: `Dismiss` and `Escalate` with confirmation before PATCH.
- Audit metadata: reviewer id, reviewed time, created/updated time when available.

### Prediction Demo

- Transaction input form matching `TransactionRequest`:
  - `transaction_id`
  - `sender_id`
  - `receiver_id`
  - `sender_balance`
  - `receiver_balance`
  - `amount`
  - `currency`
  - `timestamp`
  - `channel`
- Submit calls `POST /api/v1/predict`.
- Result view shows full `PredictionResponse`, including alert id when flagged.

### Rules View

- Show active rules from `GET /api/v1/rules`.
- Display version, rule id, typology, severity, enabled state, condition, action hint.
- Reload button may call `POST /api/v1/rules/reload`; show success/error clearly.

## Theme

Use a dark technical compliance workspace. Visual language should feel like a risk operations console: high contrast, dense but readable tables, clear severity colors, and subdued surfaces. Prioritize clarity and auditability over decoration.

## Colors

Use CSS custom properties. No hardcoded hex values in components once frontend exists.

| Role | CSS Variable | Value |
| --- | --- | --- |
| Page background | `--bg-base` | `#0B1020` |
| Surface | `--bg-surface` | `#111827` |
| Elevated surface | `--bg-elevated` | `#1F2937` |
| Primary text | `--text-primary` | `#F9FAFB` |
| Muted text | `--text-muted` | `#9CA3AF` |
| Border | `--border-default` | `#374151` |
| Primary accent | `--accent-primary` | `#38BDF8` |
| Secondary accent | `--accent-secondary` | `#A78BFA` |
| Low risk | `--risk-low` | `#22C55E` |
| Medium risk | `--risk-medium` | `#F59E0B` |
| High risk | `--risk-high` | `#F97316` |
| Critical risk | `--risk-critical` | `#EF4444` |
| Success | `--state-success` | `#22C55E` |
| Warning | `--state-warning` | `#F59E0B` |
| Error | `--state-error` | `#EF4444` |
| Info | `--state-info` | `#38BDF8` |

## Risk Visual Mapping

| Risk level | Color token | Usage |
| --- | --- | --- |
| `LOW` | `--risk-low` | Normal transaction badge, positive status |
| `MEDIUM` | `--risk-medium` | Suspicious log-only badge, caution emphasis |
| `HIGH` | `--risk-high` | Flagged alert badge and priority row marker |
| `CRITICAL` | `--risk-critical` | Highest severity alert, destructive attention color |

Review status mapping:

| Status | Visual treatment |
| --- | --- |
| `NEW` | info/neutral badge |
| `DISMISSED` | muted or success badge depending context |
| `ESCALATED` | high/critical emphasis badge |

## Typography

| Role | Font | Variable |
| --- | --- | --- |
| UI text | Inter or system sans | `--font-sans` |
| Code/IDs/numbers | JetBrains Mono or system mono | `--font-mono` |

Use tabular numerals for risk scores, amounts, timestamps, and IDs in tables.

## Border Radius

| Context | Class |
| --- | --- |
| Inline badges/buttons | `rounded-md` |
| Inputs/selects | `rounded-md` |
| Cards/panels | `rounded-lg` |
| Modals/overlays | `rounded-xl` |
| Large dashboard containers | `rounded-2xl` |

## Component Library

Recommended future stack: React + Vite + TypeScript + Tailwind + shadcn/ui. If frontend is added, prefer shadcn/ui primitives for table, dialog, button, input, select, badge, card, tabs, toast, and skeleton states. Do not hand-roll generated UI primitives unless needed.

## Layout Patterns

- **App shell**: top header with product name and auth/API status; left navigation for Dashboard, Alerts, Predict Demo, Rules, Metrics.
- **Dashboard**: responsive grid of summary cards above tables/charts.
- **Alert list**: full-width table, sticky header, compact density, row-level risk color marker.
- **Alert detail**: two-column desktop layout: left risk/evidence, right explanation/review actions; single-column on small screens.
- **Forms**: label above input, validation message below input, clear submit state.
- **Confirmation dialogs**: required before `Dismiss`, `Escalate`, or rule reload actions.
- **Toasts**: use for success/failure of review updates and reload actions; keep text specific.

## Icons

Use stroke-based icons, preferably Lucide React if frontend exists. Sizes:

- Inline text/icon: `h-4 w-4`
- Button icon: `h-4 w-4`
- Card header icon: `h-5 w-5`
- Empty state icon: `h-8 w-8`

## Copy and Data Display

- Show risk scores as decimals or percentages consistently, e.g. `0.83` or `83%`; do not mix on same screen.
- Use monospace for transaction IDs, alert IDs, rule IDs, and feature names.
- Never reveal raw secrets or API tokens in UI.
- Treat sender/receiver IDs as sensitive even when hashed; truncate by default and allow copy only when useful for debugging/demo.
- Explanation text must indicate `llm` or `template` source.
- If explanation is pending, show `Explanation pending` state rather than empty content.
- If backend returns an error envelope, display `error.code` and `error.message`; keep `details` expandable.

## Accessibility

- Maintain visible focus rings on all interactive elements.
- Do not rely on color alone for risk; include text labels.
- Confirmation dialogs must be keyboard accessible.
- Table rows need readable contrast in dark mode.
- Loading and error states must be explicit.
