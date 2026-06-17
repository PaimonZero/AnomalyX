# AnomalyX Admin Console — Sitemap & Screen Specs

## 1. Purpose

This document defines the frontend information architecture and screen-level UI specifications for the AnomalyX Admin Console. The goal is to support a data-centric, minimalist, modern interface for operations, review, testing, monitoring, and rule management.

The stack assumption is **ReactJS + shadcn/ui**, with **Vite** as the preferred frontend bootstrap tool if a new frontend project is initialized.

## 2. Product UI Principles

- Keep the admin console **operations-first**, not marketing-oriented.
- Use a **single sidebar-based app shell** for fast navigation.
- Prefer **dense but readable tables, compact charts, and clear action placement**.
- Use **cards for summaries**, **tables for investigation**, **drawers/modals for detail editing**.
- Keep small supporting information inside the **Dashboard** rather than splitting it into a dedicated page.
- Reserve standalone pages for workflows with meaningful user action, history, or state.

## 3. Sitemap

```text
AnomalyX Admin Console
├─ Dashboard
│  ├─ System Overview
│  ├─ Prometheus Metrics Preview
│  ├─ Recent Alerts
│  ├─ Recent Batch Jobs
│  ├─ Recent API Tests
│  └─ Quick Actions
│
├─ Alerts / Review Queue
│  ├─ Alert List
│  ├─ Alert Filters
│  ├─ Alert Detail Modal
│  └─ Manual Flagging / Escalate / Dismiss
│
├─ Predict Batch
│  ├─ Upload File / Paste JSON
│  ├─ Batch Config
│  ├─ Validation Preview
│  ├─ Batch Run Progress
│  ├─ Batch Results Table
│  └─ Record Detail Modal
│
├─ API Testing (Demo)
│  ├─ Endpoint Picker
│  ├─ Request Builder
│  ├─ Response Viewer
│  ├─ Request History
│  └─ Saved Samples / Presets
│
├─ Rule Engine
│  ├─ Rules List
│  ├─ Create Rule
│  ├─ Edit Rule
│  ├─ Rule Detail Drawer/Modal
│  ├─ Version History
│  └─ Reload Rules
│
├─ Model & Metrics Monitor
│  ├─ Prometheus Charts
│  ├─ Health Status
│  ├─ Latency & Throughput
│  ├─ Drift Indicators
│  └─ Explanation Quality / Fallback Stats
│
├─ Audit Log
│  ├─ Action Timeline
│  ├─ Prediction Logs
│  ├─ Rule Change Logs
│  └─ Manual Review Logs
│
└─ Settings
   ├─ Environment Status
   ├─ API Token / Auth Demo Config
   ├─ Feature Flags
   └─ Threshold / Demo Defaults
```

## 4. Page Allocation Rules

### Standalone pages
These should be separate pages because they carry enough workflow depth, state, or recurrence:
- Dashboard
- Alerts / Review Queue
- Predict Batch
- API Testing
- Rule Engine
- Model & Metrics Monitor
- Audit Log
- Settings

### Dashboard-contained widgets or overlays
These should stay in Dashboard or be implemented as modal/drawer components:
- Alert detail modal
- Batch record detail modal
- Rule detail drawer
- Prometheus summary cards
- Recent activity feed
- Quick status widgets

## 5. Shared UI Primitives

Recommended shadcn/ui components:
- `Button`
- `Card`
- `Badge`
- `Tabs`
- `Dialog`
- `AlertDialog`
- `Sheet`
- `Drawer`
- `DropdownMenu`
- `Input`
- `Textarea`
- `Select`
- `Switch`
- `Separator`
- `Table`
- `Progress`
- `Skeleton`
- `Tooltip`
- `ScrollArea`
- `Toast`

## 6. Global Layout

### Sidebar
- Fixed left sidebar
- Brand/logo area at the top
- Main navigation items in a clear vertical list
- Optional section grouping:
  - Operations: Dashboard, Alerts, Predict Batch
  - Engineering: API Testing, Rule Engine, Model & Metrics Monitor
  - Governance: Audit Log, Settings

### Header
- Page title and subtitle
- Environment badge (`Local`, `Dev`, `Demo`)
- Global search box
- Notifications icon
- User menu
- Optional reload/status indicator for active monitoring pages

### Content area
- Page-specific content rendered in a responsive grid
- Default spacing should stay airy but compact enough for dense operational data

---

# 7. Screen Specs

---

## 7.1 Dashboard

### Purpose
Provide the main operational overview of the AnomalyX system: service health, alert status, recent batch runs, recent API activity, and Prometheus-driven monitoring snapshots.

### Primary users
- Admin
- Compliance Officer
- ML/Risk Engineer

### Layout
- **Top row:** KPI cards and status chips
- **Middle row:** charts and monitoring cards
- **Bottom area:** recent alerts, recent batch jobs, recent API tests
- **Right-side or lower quick panel:** quick actions and system health summary

### Core components
- KPI cards:
  - Total predictions
  - Flagged alerts
  - High / Critical alerts
  - Avg latency
  - Explanation success rate
- Charts:
  - Requests over time
  - p95 latency
  - Decision distribution
  - Rule hit rate trend
- Status cards:
  - API health
  - Model loaded
  - Rule engine loaded
  - DB / Redis connectivity
- Recent alerts table
- Recent batch jobs table or compact list
- Recent API tests list
- Quick action buttons

### Actions
- Open alert detail modal
- Navigate to a batch job or API test
- Navigate to full Monitoring page
- Navigate to Alerts / Review Queue
- Navigate to Rule Engine

### Empty / loading / error states
- Skeleton cards while data is loading
- Empty state if no alerts or jobs exist yet
- Error banner if metrics endpoint fails, with retry action

### Notes
Keep smaller operational widgets on this page instead of splitting them into separate pages.

---

## 7.2 Alerts / Review Queue

### Purpose
Provide a dedicated review workspace for suspicious transactions and alert handling.

### Primary users
- Compliance Officer
- Admin

### Layout
- **Top filter bar:** search, status, risk level, date range, source
- **Main area:** alerts table
- **Secondary area:** optional right drawer for preview detail, or modal for full detail

### Core components
- Search input
- Filter chips/selects
- Alerts table with columns:
  - alert id
  - transaction id
  - risk score
  - risk level
  - status
  - triggered rules
  - updated at
- Bulk select controls
- Bulk action buttons
- Pagination / infinite scroll

### Actions
- Open alert detail modal
- Bulk escalate / dismiss
- Apply or clear filters
- Sort by risk score or updated time

### Empty / loading / error states
- Empty state when no alerts match the filter
- Skeleton rows during fetch
- Error toast/banner with retry if list retrieval fails

### Notes
This page should be the main compliance review entry point.

---

## 7.3 Predict Batch

### Purpose
Let users upload or paste transaction data and run batch scoring for a large set of records.

### Primary users
- Compliance Officer
- Admin
- Demo presenter

### Layout
- **Left panel:** file input, paste input, batch configuration
- **Right panel:** validation summary, progress, result summary, results table

### Core components
- File upload dropzone
- Tab switcher:
  - Upload CSV/JSON
  - Paste JSON array
- Batch configuration form
- Schema validation panel
- Progress bar
- Result summary cards
- Results table
- Export/download button

### Actions
- Preview payload before run
- Run batch
- Cancel / reset input
- Export results
- Open record detail modal

### Empty / loading / error states
- Drag-and-drop empty state
- Validation error panel for malformed rows
- Loading state during batch processing
- Partial failure state with failed row count and retry option

### Notes
If batch jobs are short and light, the page can stay client-oriented; if jobs become long, treat it as async job state with polling.

---

## 7.4 API Testing (Demo)

### Purpose
Provide a Postman-like demo workspace for testing AnomalyX endpoints individually.

### Primary users
- Admin
- Engineer
- Demo presenter

### Layout
- **Left panel:** endpoint picker and request builder
- **Right panel:** response viewer
- **Bottom area:** request history and saved samples

### Core components
- Method selector
- Endpoint selector
- Auth/token input
- Headers editor
- JSON body editor
- Query params editor
- Example payload presets
- Send button
- Save request button
- Response status badge
- Latency badge
- JSON response viewer
- History list

### Supported endpoints
- `/health`
- `/metrics`
- `/api/v1/predict`
- `/api/v1/batch-score`
- `/api/v1/alerts`
- `/api/v1/alerts/{id}`
- `/api/v1/alerts/{id}/status`
- `/api/v1/rules`
- `/api/v1/rules/reload`

### Actions
- Send request
- Load example payload
- Copy response
- Replay history item
- Save sample preset

### Empty / loading / error states
- Empty sample state for new users
- Loading spinner while request is in flight
- Error panel for non-2xx responses with readable payload

### Notes
This page should be compact, stable in height, and optimized for repeat demo use.

---

## 7.5 Rule Engine

### Purpose
Manage AML rules through CRUD operations, validation, versioning, and reload flows.

### Primary users
- ML/Risk Engineer
- Admin

### Layout
- **Top action row:** search, filters, create button, reload button
- **Main area:** rules table
- **Right drawer or modal:** rule detail / edit form

### Core components
- Search box
- Filter chips:
  - severity
  - enabled
  - typology
  - version
- Rules table:
  - rule id
  - typology
  - severity
  - condition summary
  - enabled
  - updated at
  - actions
- Create/Edit form
- Condition editor / DSL textarea
- Validation helper text
- Version history panel
- Reload status indicator

### Actions
- Create rule
- Edit rule
- Delete rule
- Enable / disable rule
- Duplicate rule
- Reload active rules
- Test rule against sample context

### Empty / loading / error states
- Empty table state when no rules are defined
- Inline field validation errors
- Conflict / reload failure banner if rule validation fails

### Notes
Use a drawer for editing when possible to preserve table context; use a full page form only if the rule editor grows too complex.

---

## 7.6 Model & Metrics Monitor

### Purpose
Provide a focused observability page for Prometheus metrics, system health, drift indicators, and explanation quality.

### Primary users
- ML/Risk Engineer
- Admin

### Layout
- KPI summary row
- Chart grid
- Health/drift panels
- Metrics table or timeline

### Core components
- Prometheus chart cards
- Health status cards
- Latency histogram or timeseries chart
- Throughput chart
- Drift indicators
- Explanation success / fallback cards
- Rule hit trend chart

### Actions
- Refresh metrics
- Change time range
- Drill into chart details

### Empty / loading / error states
- Skeleton charts during loading
- Message when no metric window is available
- Retry action if scrape data is unavailable

### Notes
If space is limited, keep lightweight health previews on Dashboard and place deep observability here.

---

## 7.7 Audit Log

### Purpose
Keep a traceable activity history for predictions, rule changes, review actions, and system events.

### Primary users
- Admin
- Compliance Officer
- ML/Risk Engineer

### Layout
- Filter bar at top
- Main timeline or table
- Optional detail drawer

### Core components
- Search input
- Filter selects:
  - action type
  - actor role
  - date range
- Activity timeline / table
- Event detail drawer
- Download/export button

### Event categories
- Prediction event
- Manual flag event
- Escalate / dismiss event
- Rule create / update / delete
- Rule reload
- API test execution
- Batch job completion

### Actions
- Inspect event detail
- Filter by actor or action
- Export audit records

### Empty / loading / error states
- Empty state if audit stream is not yet populated
- Skeleton rows during load
- Error banner if backend log retrieval fails

### Notes
This page reinforces traceability and makes the product feel complete for the AML domain.

---

## 7.8 Settings

### Purpose
Expose demo and environment-related configuration for the admin console.

### Primary users
- Admin
- Demo presenter

### Layout
- Sectioned settings cards
- Simple form groups
- Save button area

### Core components
- Environment status card
- Auth token demo config
- Feature flags
- Threshold / demo defaults
- Provider / repository status
- Save / reset buttons

### Actions
- Save settings
- Reset to default
- Copy demo token
- Toggle feature flags

### Empty / loading / error states
- Settings loading skeleton
- Inline validation for invalid values
- Save success toast / error toast

### Notes
Keep this page simple; it is mainly for demo control and configuration visibility.

---

## 7.9 Alert Detail Modal

### Purpose
Show the full context of a flagged transaction and allow a privileged user to manually flag, escalate, or dismiss it.

### Trigger points
- Click from Dashboard recent alerts
- Click from Alerts / Review Queue
- Click from Predict Batch results

### Layout
- **Left column:** transaction and alert summary
- **Right column:** explanation and evidence
- Footer with action buttons

### Core components
- Alert summary block
- Risk badge
- Risk score
- Triggered rules list
- Top contributing features list
- Explanation text
- Audit trail / timestamps
- Reviewer note input
- Action buttons:
  - Manual Flag
  - Escalate
  - Dismiss
  - Close

### Manual flagging flow
1. User clicks **Manual Flag**
2. Confirmation dialog appears
3. User selects reason and optional note
4. Submission updates status and writes audit trail
5. Toast confirms success and table row updates

### Notes
This modal is a key operational touchpoint and should be designed as a decision surface, not just an information panel.

---

## 7.10 Rule Detail Drawer / Modal

### Purpose
Provide deeper rule information without leaving the rules table context.

### Core components
- Rule metadata
- Condition preview
- Example trigger conditions
- Version history
- Last reload result
- Enable/disable toggle
- Edit button

### Notes
Use a drawer for fast context retention; use a modal only for lightweight previews.

---

## 7.11 Batch Record Detail Modal

### Purpose
Show a single scored record from the batch results with enough detail for review and manual action.

### Core components
- Transaction summary
- Risk score and level
- Triggered rules
- Top features
- Explanation / fallback text
- Manual flag actions

### Notes
This can reuse most of the same content structure as the alert detail modal.

---

# 8. Recommended Frontend Structure

If the frontend is initialized with React + Vite, a practical folder structure is:

```text
src/
├─ app/
│  ├─ routes/
│  ├─ layout/
│  └─ providers/
├─ components/
│  ├─ ui/
│  ├─ common/
│  ├─ charts/
│  └─ data-table/
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
├─ hooks/
├─ services/
└─ types/
```

This keeps page-specific logic isolated while sharing reusable primitives through the shadcn/ui layer.

## 9. Summary

The application should ship as a single admin console with a shared sidebar layout. Smaller support views belong inside the Dashboard. Larger workflows deserve dedicated pages. The result is a product that is easier to demo, easier to navigate, and better aligned with the AnomalyX backend capabilities and AML operational workflow.
