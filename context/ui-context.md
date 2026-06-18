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

---

## Theme

Two modes: **dark** (default, primary) and **light** (optional toggle). Both share the same warm, professional character — a risk operations console that feels precise and trustworthy rather than harsh or decorative. Inspired by Claude's UI language: warm neutrals, a coral/terracotta accent, clean typographic hierarchy, and restrained use of color.

- Dark mode: deep navy backgrounds, warm off-white text, muted warm borders.
- Light mode: warm cream backgrounds, deep charcoal text, the same coral accent.
- Accent color is consistent across both modes — Claude-signature coral `#CC785C`.
- Risk level colors are semantically invariant; only adjusted slightly for contrast per mode.

Implement mode switching via a `data-theme="dark" | "light"` attribute on `<html>` and a single CSS custom property block per theme.

---

## Colors

### Dark Mode (default)

| Role | CSS Variable | Value |
|------|-------------|-------|
| Page background | `--bg-base` | `#0D0F17` |
| Surface | `--bg-surface` | `#151720` |
| Elevated surface | `--bg-elevated` | `#1E2130` |
| Subtle surface | `--bg-subtle` | `#252838` |
| Primary text | `--text-primary` | `#F2F0EB` |
| Secondary text | `--text-secondary` | `#C8C5BC` |
| Muted text | `--text-muted` | `#8A8880` |
| Border default | `--border-default` | `#2A2D3E` |
| Border subtle | `--border-subtle` | `#1E2130` |
| Primary accent | `--accent-primary` | `#CC785C` |
| Accent hover | `--accent-primary-hover` | `#D98B70` |
| Accent muted | `--accent-primary-muted` | `#3D2820` |
| Secondary accent | `--accent-secondary` | `#9B8AFB` |
| Secondary muted | `--accent-secondary-muted` | `#28243D` |

### Light Mode

| Role | CSS Variable | Value |
|------|-------------|-------|
| Page background | `--bg-base` | `#F5F4EF` |
| Surface | `--bg-surface` | `#FFFFFF` |
| Elevated surface | `--bg-elevated` | `#FAFAF7` |
| Subtle surface | `--bg-subtle` | `#EEECEA` |
| Primary text | `--text-primary` | `#1A1B26` |
| Secondary text | `--text-secondary` | `#3D3E4E` |
| Muted text | `--text-muted` | `#7A7A80` |
| Border default | `--border-default` | `#DDDBD4` |
| Border subtle | `--border-subtle` | `#EEECEA` |
| Primary accent | `--accent-primary` | `#CC785C` |
| Accent hover | `--accent-primary-hover` | `#B8674D` |
| Accent muted | `--accent-primary-muted` | `#FAE8E2` |
| Secondary accent | `--accent-secondary` | `#6B5FD6` |
| Secondary muted | `--accent-secondary-muted` | `#EDEAFC` |

### Risk & Status Colors (shared across modes)

Risk level colors are intentionally bold and consistent across both modes so severity is instantly recognizable.

| Role | CSS Variable | Dark value | Light value |
|------|-------------|-----------|------------|
| Low risk | `--risk-low` | `#3DB87A` | `#1E8A55` |
| Medium risk | `--risk-medium` | `#E8A842` | `#C07A10` |
| High risk | `--risk-high` | `#E86A2E` | `#C04E18` |
| Critical risk | `--risk-critical` | `#E84040` | `#C01C1C` |
| Low muted bg | `--risk-low-muted` | `#0F2B1C` | `#E6F5EE` |
| Medium muted bg | `--risk-medium-muted` | `#2B1E08` | `#FDF2E0` |
| High muted bg | `--risk-high-muted` | `#2B1208` | `#FDEEE6` |
| Critical muted bg | `--risk-critical-muted` | `#2B0808` | `#FDEAEA` |
| Success | `--state-success` | `#3DB87A` | `#1E8A55` |
| Warning | `--state-warning` | `#E8A842` | `#C07A10` |
| Error | `--state-error` | `#E84040` | `#C01C1C` |
| Info | `--state-info` | `#5AADDC` | `#1E7FAD` |

### CSS Implementation

```css
:root,
[data-theme="dark"] {
  --bg-base: #0D0F17;
  --bg-surface: #151720;
  --bg-elevated: #1E2130;
  --bg-subtle: #252838;
  --text-primary: #F2F0EB;
  --text-secondary: #C8C5BC;
  --text-muted: #8A8880;
  --border-default: #2A2D3E;
  --border-subtle: #1E2130;
  --accent-primary: #CC785C;
  --accent-primary-hover: #D98B70;
  --accent-primary-muted: #3D2820;
  --accent-secondary: #9B8AFB;
  --accent-secondary-muted: #28243D;
  --risk-low: #3DB87A;
  --risk-medium: #E8A842;
  --risk-high: #E86A2E;
  --risk-critical: #E84040;
  --risk-low-muted: #0F2B1C;
  --risk-medium-muted: #2B1E08;
  --risk-high-muted: #2B1208;
  --risk-critical-muted: #2B0808;
  --state-success: #3DB87A;
  --state-warning: #E8A842;
  --state-error: #E84040;
  --state-info: #5AADDC;
}

[data-theme="light"] {
  --bg-base: #F5F4EF;
  --bg-surface: #FFFFFF;
  --bg-elevated: #FAFAF7;
  --bg-subtle: #EEECEA;
  --text-primary: #1A1B26;
  --text-secondary: #3D3E4E;
  --text-muted: #7A7A80;
  --border-default: #DDDBD4;
  --border-subtle: #EEECEA;
  --accent-primary: #CC785C;
  --accent-primary-hover: #B8674D;
  --accent-primary-muted: #FAE8E2;
  --accent-secondary: #6B5FD6;
  --accent-secondary-muted: #EDEAFC;
  --risk-low: #1E8A55;
  --risk-medium: #C07A10;
  --risk-high: #C04E18;
  --risk-critical: #C01C1C;
  --risk-low-muted: #E6F5EE;
  --risk-medium-muted: #FDF2E0;
  --risk-high-muted: #FDEEE6;
  --risk-critical-muted: #FDEAEA;
  --state-success: #1E8A55;
  --state-warning: #C07A10;
  --state-error: #C01C1C;
  --state-info: #1E7FAD;
}
```

---

## Risk Visual Mapping

| Risk level | CSS variable | Badge appearance |
|------------|-------------|-----------------|
| `LOW` | `--risk-low` | Green text on `--risk-low-muted` background |
| `MEDIUM` | `--risk-medium` | Amber text on `--risk-medium-muted` background |
| `HIGH` | `--risk-high` | Orange text on `--risk-high-muted` background |
| `CRITICAL` | `--risk-critical` | Red text on `--risk-critical-muted` background |

Review status mapping:

| Status | Visual treatment |
|--------|-----------------|
| `NEW` | `--state-info` text, neutral border |
| `DISMISSED` | `--text-muted` text, `--bg-subtle` background |
| `ESCALATED` | `--risk-critical` text, `--risk-critical-muted` background |
| `REVIEWED` | `--state-success` text, `--risk-low-muted` background |

---

## Typography

| Role | Font | Variable |
|------|------|----------|
| UI text | Inter, system-ui, sans-serif | `--font-sans` |
| Code / IDs / numbers | JetBrains Mono, ui-monospace, monospace | `--font-mono` |

Rules:
- Use tabular numerals (`font-variant-numeric: tabular-nums`) for risk scores, amounts, timestamps, and IDs in tables.
- Heading hierarchy: `text-xl font-semibold` for page titles, `text-sm font-medium` for card headers, `text-xs` for labels/captions.
- Body text: `text-sm` for table rows and most content, `text-base` for forms and readable paragraphs.
- All IDs (transaction, alert, rule): render in `font-mono text-xs`.

---

## Border Radius

| Context | Tailwind class |
|---------|---------------|
| Inline badges | `rounded-md` |
| Buttons | `rounded-md` |
| Inputs / selects | `rounded-md` |
| Cards / panels | `rounded-lg` |
| Modals / overlays | `rounded-xl` |
| Large containers | `rounded-2xl` |
| Sidebar | square edges — `rounded-none` |

---

## Component Library

Stack: **React + Vite + TypeScript + Tailwind CSS + shadcn/ui**

Prefer shadcn/ui primitives. Do not hand-roll:

| Use case | shadcn component |
|----------|-----------------|
| Data tables | `Table`, `TableHeader`, `TableRow`, `TableCell` |
| Dialogs / confirmations | `Dialog`, `AlertDialog` |
| Slide-in panels | `Sheet` |
| Risk/status labels | `Badge` |
| Summary containers | `Card`, `CardHeader`, `CardContent` |
| Page sections | `Separator` |
| Form fields | `Input`, `Textarea`, `Select`, `Switch` |
| Feedback | `Toast` (via `useToast`) |
| Loading | `Skeleton` |
| Hints | `Tooltip` |
| Tab switching | `Tabs`, `TabsList`, `TabsTrigger`, `TabsContent` |
| Progress | `Progress` |
| Scrollable areas | `ScrollArea` |
| Overflow menus | `DropdownMenu` |

---

## Layout Patterns

- **App shell**: fixed left sidebar (240px) + top header (56px) + scrollable content area.
- **Sidebar sections**: Operations (Dashboard, Alerts, Predict Batch) / Engineering (API Testing, Rule Engine, Model & Metrics Monitor) / Governance (Audit Log, Settings).
- **Header**: page title + subtitle left; environment badge + search + notifications + theme toggle + user menu right.
- **Dashboard**: `grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4` KPI row, then `grid-cols-1 xl:grid-cols-3` for charts + health panel.
- **Alert list**: full-width table, sticky filter bar, compact density (`text-sm`), left border color stripe per risk level.
- **Alert detail**: `grid grid-cols-1 lg:grid-cols-2` — left: risk summary + rule evidence + features; right: explanation + review actions.
- **Forms**: label above input (`mb-1.5 text-xs text-muted`), validation message below (`mt-1 text-xs text-error`), clear submit state.
- **Confirmation dialogs**: required before `Dismiss`, `Escalate`, rule delete, or rule reload.
- **Toasts**: success/failure for review updates, reload actions; text must be specific (e.g., "Alert ALT-0042 escalated").

---

## Icons

Use **Lucide React** — stroke-based, consistent weight. Size scale:

| Context | Class |
|---------|-------|
| Inline with text | `h-4 w-4` |
| Button icon | `h-4 w-4` |
| Card header | `h-5 w-5` |
| Sidebar nav item | `h-5 w-5` |
| Empty state | `h-10 w-10 text-muted` |
| Page-level status | `h-6 w-6` |

Common icon assignments:
- Dashboard → `LayoutDashboard`
- Alerts → `ShieldAlert`
- Predict Batch → `Upload`
- API Testing → `Terminal`
- Rule Engine → `GitBranch`
- Monitoring → `Activity`
- Audit Log → `ScrollText`
- Settings → `Settings2`
- Risk HIGH/CRITICAL → `AlertTriangle`
- Escalate → `ArrowUpCircle`
- Dismiss → `XCircle`
- Reload → `RefreshCw`
- Copy → `Copy`
- Export → `Download`

---

## Copy and Data Display

- Risk scores: display as decimals (`0.83`) in tables; as percentages (`83%`) in summary cards. Never mix on the same screen.
- Use `font-mono text-xs` for transaction IDs, alert IDs, rule IDs, and feature names.
- Never reveal raw API tokens. Show a masked placeholder (`sk-••••••••`) with a copy-icon that copies the real value.
- Sender/receiver IDs: truncate to first 8 chars + `…` by default; full value on hover tooltip or copy action.
- Explanation text must show `llm` or `template` source badge next to the text.
- If explanation is pending, show `Explanation pending…` with a subtle pulse animation, not an empty area.
- If backend returns an error envelope, display `error.code` as a badge and `error.message` as body text; keep `details` in a collapsible `<details>` element.
- Amounts: always show currency code. Right-align numeric columns.
- Timestamps: `yyyy-MM-dd HH:mm:ss` in tables; relative (`2h ago`) in activity feeds with full timestamp on tooltip.

---

## Theme Toggle

- Provide a `ThemeToggle` button in the header (sun/moon icon).
- Persist preference to `localStorage` under key `anomalyx-theme`.
- Default to dark mode unless the user's OS prefers light (`prefers-color-scheme: light`) and no stored preference exists.
- The toggle sets `data-theme` on `<html>`.

---

## Accessibility

- Maintain visible focus rings on all interactive elements (use `ring-2 ring-accent-primary ring-offset-2`).
- Never rely on color alone for risk level — always include a text label alongside color.
- Confirmation dialogs must be keyboard accessible (Escape to cancel, Enter to confirm).
- Table rows must have readable contrast in both modes (≥ 4.5:1 ratio against the surface).
- Loading and error states must be explicit — no silent empty spaces.
- Use `aria-label` on icon-only buttons.
- `role="status"` on toast messages.
