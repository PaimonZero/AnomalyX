# API Testing (Demo) Screen Spec

## Purpose
The API Testing screen provides a Postman-like demo workspace for testing all AnomalyX endpoints interactively. It is designed for demo presenters and engineers to construct requests, send them with live JWT auth, and inspect the response — without leaving the admin console.

## Primary users
- Admin
- ML/Risk Engineer
- Demo presenter / Mentor

## Goals
- Let users construct and send requests to all AnomalyX endpoints
- Pre-populate example payloads so the demo runs immediately without manual typing
- Display response clearly — status, latency, JSON body, headers
- Preserve request history for replay and comparison
- Show the API error envelope format clearly when errors occur

---

## Layout

### Three-zone layout
- **Left panel (35%)**: endpoint picker + request builder
- **Right panel (65%)**: response viewer
- **Bottom drawer (collapsible)**: request history + saved sample presets

---

## Core components

### Left panel — Request builder

#### Endpoint selector
- Endpoint dropdown (pre-populated with all 9 supported endpoints)
- Method badge auto-fills based on selection (GET / POST / PATCH); not editable — determined by endpoint

#### Supported endpoints (exact paths)

| Method | Path | Auth required | Description |
|--------|------|--------------|-------------|
| GET | `/health` | No | Liveness / readiness check |
| GET | `/metrics` | No | Prometheus metrics scrape |
| POST | `/api/v1/predict` | Yes (JWT) | Real-time transaction scoring |
| POST | `/api/v1/batch-score` | Yes (JWT) | Batch scoring |
| GET | `/api/v1/alerts` | Yes (JWT) | List / filter alerts |
| GET | `/api/v1/alerts/{id}` | Yes (JWT) | Single alert detail |
| PATCH | `/api/v1/alerts/{id}/status` | Yes (JWT) | Escalate or dismiss an alert |
| GET | `/api/v1/rules` | Yes (JWT) | Active rule configuration |
| POST | `/api/v1/rules/reload` | Yes (JWT) | Hot-reload rule set |

#### Auth section
- Auth token input field (masked, `type="password"`) — pre-filled from Settings if a demo token is configured
- "Use saved token" toggle — loads token from Settings
- Token is sent as `Authorization: Bearer {token}` header

#### Path parameter inputs
- Appear dynamically when endpoint contains `{id}` — e.g. alert ID field

#### Query parameters editor
- Key-value table (add/remove rows) for GET endpoints
- Common params pre-suggested: `status`, `risk_level`, `page`, `limit` for `/api/v1/alerts`

#### Request headers editor
- Key-value table for custom headers
- `Content-Type: application/json` auto-added for POST/PATCH
- `Idempotency-Key` header field (optional, shown as a helper for `/api/v1/predict`)

#### JSON body editor
- Syntax-highlighted code editor for POST/PATCH endpoints
- Auto-populated with example payload when endpoint is selected
- "Format JSON" button to pretty-print
- Validation indicator: green checkmark if valid JSON, red X + error position if malformed

#### Example payload presets (per endpoint)

**POST /api/v1/predict — example:**
```json
{
  "transaction_id": "8f1c3a2b-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
  "sender_id": "h:3a9f2b8c1d4e5f6a7b8c9d0e1f2a3b4c",
  "receiver_id": "h:7b2c8d3e4f5a6b7c8d9e0f1a2b3c4d5e",
  "sender_balance": 15000000,
  "receiver_balance": 200000,
  "amount": 390000000,
  "currency": "VND",
  "timestamp": "2026-05-30T09:14:03+07:00",
  "channel": "TRANSFER",
  "device_id": "device-demo-001",
  "location_country": "VN",
  "location_region": "HN"
}
```

**PATCH /api/v1/alerts/{id}/status — example:**
```json
{
  "status": "ESCALATED",
  "reviewer_id": "officer-demo-01",
  "note": "Confirmed structuring pattern based on rule R-STRUCT-01"
}
```

**POST /api/v1/rules/reload — body:** (empty, JWT-authenticated POST)

- Multiple named presets per endpoint: "Normal transaction", "Structuring pattern", "High-risk batch" etc.

#### Send + Save
- **Send** button (primary) — fires the request
- **Save request** button — saves current request as a named preset

---

### Right panel — Response viewer

#### Status summary bar
- HTTP status badge (e.g. `200 OK` in green, `400 Bad Request` in red, `401 Unauthorized` in amber)
- Latency badge (e.g. `142 ms`), tabular numerals
- Response size (bytes)
- Copy response button

#### Response tabs
- **Body** (default) — pretty-printed JSON with syntax highlighting; collapsible nested objects
- **Headers** — key-value table of response headers
- **Raw** — plain text response

#### Error envelope display
When the backend returns an error, render it in a structured format:
```text
Error: {error.code}
Message: {error.message}
▶ Details (expandable): {error.details}
```

#### Response body for `/api/v1/predict` success
Render the prediction response fields with semantic styling:
- `risk_level` badge colored by level
- `is_flagged` boolean as a ✓ or ✗ chip
- `risk_score` as a large decimal
- `triggered_rules` as a list of rule chips with severity
- `top_features` as a mini table: name | value | contribution bar
- `explanation: null` shown as "Explanation pending (async)…"
- `alert_id` in monospace if flagged

---

### Bottom section — History + Presets

#### Request history list (last 20)
- Each item: method badge, endpoint path, status code, latency, timestamp
- Click to replay: populates the request builder with that exact request
- Clear history button

#### Saved sample presets
- Named presets per endpoint
- Click to load: populates body, params, and headers
- Delete preset button

---

## Interaction model
- Selecting an endpoint auto-populates method, path, and example payload
- Sending a request updates the response panel without shifting the layout
- History items work as single-click demo replay
- Failed requests (non-2xx) render the error envelope clearly, not as a raw text dump

---

## States

### Loading (request in flight)
- Send button disabled + spinner
- Response panel shows skeleton while waiting

### Empty (initial)
- Response panel: placeholder text "Send a request to see the response here"
- Pre-load the `/api/v1/predict` endpoint with the structuring example payload as the default view

### Error (non-2xx response)
- Response panel shows the HTTP status badge in red
- Error envelope rendered in the structured format above
- No toast for HTTP errors — the response panel IS the error display

### Auth failure (401 / 403)
- Distinct amber badge on status
- Hint: "Check your auth token in the request builder or Settings"

---

## Notes
- This page should feel like a compact, polished demo tool — not a full API IDE. Keep height stable; the layout should not shift when a response arrives.
- JWT token is never displayed in plain text — only masked (`••••••••`). Copy action copies the real value.
- `Idempotency-Key` header hint: "If you resend with the same `transaction_id`, the system returns the cached decision (idempotency)."
- Channel enum values to show in payload hints: `PAYMENT` · `TRANSFER` · `CASH_OUT` · `CASH_IN` · `DEBIT`
- Amount near 400,000,000 VND (CTR threshold) is a useful demo value — include in the "Structuring pattern" preset.
