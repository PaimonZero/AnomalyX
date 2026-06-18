# Settings Screen Spec

## Purpose
The Settings screen exposes environment configuration, demo control parameters, service integration status, and decision threshold management for the AnomalyX Admin Console. It is primarily used by the demo presenter and admin to prepare the system for a demo run or to verify the current configuration.

## Primary users
- Admin (primary)
- Demo presenter / Mentor

## Goals
- Show current environment and backend mode clearly
- Allow demo token management without revealing secrets
- Expose configurable decision thresholds (τ_medium, τ_flag)
- Show CTR threshold (regulatory constant)
- Display LLM provider configuration and status
- Expose feature flags that affect system behavior
- Keep the page intentionally simple — not a complex admin panel

---

## Layout

- Sectioned settings cards in a single-column or 2-column grid
- Each section is a `Card` with a header icon, title, and a form or status group
- Footer: Save · Reset to defaults · (section-specific) Copy actions

---

## Sections

### 1. Environment Status card

Read-only status display:

| Field | Value | Note |
|-------|-------|------|
| Environment | `LOCAL` · `DEV` · `DEMO` badge | From `ENVIRONMENT` env var |
| Backend mode | `in_memory` · `postgres` · `supabase` | From `ALERT_REPOSITORY` |
| Idempotency store | `in_memory` · `redis` | From `IDEMPOTENCY_STORE` |
| ML mode | `mock` · `live` | From `MOCK_ML_ENABLED` |
| Active model version | `mock-ml-v1` or registered version | From model registry |
| Active rule version | Rule set version string | From `GET /api/v1/rules` |
| Active rules count | Integer | From `GET /api/v1/rules` |

### 2. Auth & API Token card

| Field | Type | Note |
|-------|------|------|
| Demo auth token | Masked input (`••••••••`) | Copy button copies real value; never displayed in plain text |
| JWT secret status | Read-only: "Configured" or "Missing" badge | Whether `JWT_SECRET_KEY` env var is set |
| Token expiry | Optional: ISO timestamp or "No expiry" | |

Actions:
- **Copy token** — copies to clipboard, shows "Copied!" toast for 2 seconds
- No "reveal" option — tokens are never shown in the UI (SEC-02)

### 3. Decision Thresholds card

These thresholds map `risk_score` to `risk_level` and control the `is_flagged` outcome:

| Threshold | Field | Default | Description |
|-----------|-------|---------|-------------|
| τ_medium | Number input (0.00–1.00, step 0.01) | `0.40` | Scores ≥ τ_medium → MEDIUM (log-only) |
| τ_flag | Number input (0.00–1.00, step 0.01) | `0.70` | Scores ≥ τ_flag → HIGH + is_flagged = true |

Validation:
- τ_medium must be < τ_flag
- Both must be in range [0.01, 0.99]
- Inline validation error: "τ_medium must be less than τ_flag"

Read-only reference card showing the full decision matrix:

| Rule output | ML risk_score | risk_level | is_flagged |
|-------------|-------------|-----------|-----------|
| CRITICAL rule | Any | CRITICAL | true |
| HIGH rule | Any | HIGH | true |
| None / MINOR | ≥ τ_flag | HIGH | true |
| MINOR rule | τ_medium ≤ score < τ_flag | MEDIUM | false |
| None | τ_medium ≤ score < τ_flag | MEDIUM | false |
| None / MINOR | < τ_medium | LOW | false |

### 4. Regulatory Constants card

Read-only (not user-editable — these are locked per TDD §10):

| Constant | Value | Source |
|----------|-------|--------|
| CTR reporting threshold | 400,000,000 VND | Decision 11/2023/QĐ-TTg |
| Structuring detection window | 24 hours | Rule R-STRUCT-01 |
| Velocity baseline window | 7 days | Feature catalog |

Note displayed: "These constants are locked per Vietnamese AML regulation and cannot be changed without a code change."

### 5. LLM Provider card

| Field | Type | Note |
|-------|------|------|
| LLM provider | Read-only label | `OpenAI` · `Anthropic` · `Local model` — from `.env` |
| API key status | Read-only badge | "Configured" (green) or "Missing" (red) — never shows the key itself |
| Explanation language | Select | `bilingual (Vietnamese/English)` · `English only` · `Vietnamese only` |
| Async explanation | Toggle (read-only) | Always true — LLM is async per PER-02 |
| Fallback behavior | Read-only | "Template fallback on timeout/error" |
| LLM sandbox note | Informational | "API keys are injected via .env and excluded from version control (SEC-02)" |

### 6. Feature Flags card

| Flag | Toggle | Description |
|------|--------|-------------|
| Mock ML enabled | Switch | `MOCK_ML_ENABLED` — use deterministic mock predictor instead of live model |
| Idempotency enforcement | Switch | Whether duplicate `transaction_id` returns cached response |
| Async LLM explanations | Read-only (always ON) | Per PER-02 — not user-configurable |
| Demo mode | Switch | Enables pre-seeded demo data and example payloads in API Testing |

### 7. Provider / Repository Status card

Live connectivity status chips for each external dependency:

| Service | Status | Config reference |
|---------|--------|-----------------|
| PostgreSQL | UP / DOWN / N/A | `ALERT_REPOSITORY=postgres` |
| Redis | UP / DOWN / N/A | `IDEMPOTENCY_STORE=redis` |
| LLM API | UP / DOWN / N/A | Last successful call |
| Supabase | UP / DOWN / N/A (optional) | `ALERT_REPOSITORY=supabase` |

"N/A" shown when service is not configured (e.g., `ALERT_REPOSITORY=in_memory`).

---

## Footer actions

- **Save settings** — validates and persists threshold + language settings; shows success toast: "Settings saved"
- **Reset to defaults** — requires AlertDialog confirmation ("Reset all settings to defaults? This will restore τ_medium=0.40 and τ_flag=0.70."); shows success toast on completion
- **Copy demo token** — available at the top of the Auth card

---

## States

### Loading
- Skeleton cards while `/health` and settings data load

### Empty
- Show defaults if no config has been explicitly set; badge each default with a subtle "default" chip

### Error
- Save failure: inline error banner: "Save failed — {error.code}: {error.message}" + Retry
- If required env vars are missing (`AUTH_TOKEN`, `JWT_SECRET_KEY`): red badge on Auth card with message "Required variable missing — check your .env file"
- Connectivity failures shown as red DOWN chips in the repository status card

---

## Notes
- This page is intentionally narrow in scope — it is for demo readiness and environment inspection, not a full admin control panel.
- Never show raw secrets, API keys, or auth tokens in the UI, even on this settings page (SEC-02). All sensitive values are masked; copy-to-clipboard is the only access pattern.
- The `Reset to defaults` action only resets threshold and UI preferences — it does not reset the database, clear alerts, or change backend env vars.
- The CTR threshold card is read-only and labeled explicitly as a legal constant to communicate regulatory grounding to the Mentor/Evaluator.
