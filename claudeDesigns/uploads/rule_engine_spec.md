# Rule Engine Screen Spec

## Purpose
The Rule Engine screen provides full CRUD management for AML detection rules, supporting creation, editing, enable/disable, validation, version awareness, and hot-reload — fulfilling UC-05 (Update rule config) from the PRD.

## Primary users
- ML/Risk Engineer (primary)
- Admin

## Goals
- Manage the 6+ AML rules as first-class operational assets
- Support creation and editing via a YAML-aware form
- Provide safe hot-reload with visible success/failure state
- Show rule version history and active rule set metadata
- Allow rule testing against a sample transaction context

---

## Layout

### Top action row
- Page title "Rule Engine" + subtitle with active rule count and rule_version
- Left: search bar + filter chips
- Right: **Create Rule** button (primary) + **Reload Rules** button (secondary with ↺ icon)

### Main area
- Rules table (full width)
- Rule detail drawer (slides in from right on row click / edit)

---

## Core components

### Filters and search

| Filter | Type | Options |
|--------|------|---------|
| Search | Text | Matches `rule_id` or `typology` |
| Severity | Multi-select | CRITICAL · HIGH · MEDIUM · MINOR |
| Enabled | Select | All · Enabled only · Disabled only |
| Typology | Multi-select | structuring · smurfing · rapid_movement · layering · velocity_anomaly · geo_device_anomaly |
| Version | Select | Current · All versions |

### Rules table

| Column | Field | Display |
|--------|-------|---------|
| Rule ID | `rule_id` | Monospace (e.g. `R-STRUCT-01`) |
| Typology | `typology` | Human-readable label + AML pattern chip |
| Severity | `severity` | Colored badge: CRITICAL=red, HIGH=orange, MEDIUM=amber, MINOR=muted |
| Condition | `condition` (truncated) | Mono code snippet, 60 chars max + "…" |
| Window | `window` | Duration string (e.g. `24h`) |
| Action hint | `action_hint` | `FLAG` · `BLOCK` · `ALLOW` chip |
| Enabled | `enabled` | Toggle switch (inline fast-toggle) |
| Updated | `updated_at` | Relative with full timestamp tooltip |
| Actions | — | ⋯ menu: Edit · Duplicate · Delete · View history |

### Initial rule set (from TDD §4.3 — always present in the table)

| Rule ID | Typology | Severity | Condition (informal) |
|---------|----------|----------|---------------------|
| `R-STRUCT-01` | structuring | HIGH | ≥3 transactions just below 400M VND within 24h |
| `R-SMURF-01` | smurfing | HIGH | distinct_receivers_1h ≥ N and sum_amount_1h ≥ X |
| `R-RAPID-01` | rapid_movement | HIGH | in→out within 60 min, repeated ≥ k times |
| `R-LAYER-01` | layering | MEDIUM | chain_depth ≥ 3 with near-equal amounts |
| `R-VELO-01` | velocity_anomaly | MEDIUM | velocity_vs_baseline_ratio > 10 |
| `R-GEO-01` | geo_device_anomaly | MEDIUM | new device or geo anomaly or impossible travel (partial — requires Redis history) |

### Rule Create / Edit Form (inside the drawer)

#### Form fields

| Field | Input type | Validation |
|-------|-----------|-----------|
| Rule ID | Text input (mono font) | Required; unique; pattern `[A-Z]-[A-Z]{3,6}-[0-9]{2}` |
| Typology | Select | Required; from: structuring · smurfing · rapid_movement · layering · velocity_anomaly · geo_device_anomaly |
| Severity | Select | Required; from: CRITICAL · HIGH · MEDIUM · MINOR |
| Condition | Textarea (mono font, DSL) | Required; validated against feature whitelist |
| Window | Text input | Optional duration string (e.g. `24h`, `1h`, `7d`) |
| Action hint | Select | Required; from: FLAG · BLOCK · ALLOW |
| Enabled | Switch | Default: true |

#### DSL condition editor hints
Inline helper panel listing allowed feature names:
- Transaction: `log_amount`, `hour_of_day`, `is_round_amount`, `amount_to_threshold_ratio`
- Velocity: `tx_count_1h`, `tx_count_24h`, `tx_count_7d`, `sum_amount_1h`, `sum_amount_24h`, `std_amount`
- Counterparty: `distinct_receivers_1h`, `distinct_receivers_24h`, `fan_out`, `fan_in`
- Behavioural: `amount_zscore_vs_user`, `velocity_vs_baseline_ratio`
- Sequence: `rapid_inout_flag`, `chain_depth`
- Structuring: `count_just_below_threshold_24h`, `sum_just_below`

Allowed operators: `and`, `or`, `not`, `>`, `>=`, `<`, `<=`, `==`, `!=`, numeric literals.
Note: conditions are sandboxed — arbitrary code, imports, or function calls are not permitted.

#### YAML preview tab
Show the rule as it would appear in `configs/rules.yaml`:
```yaml
- id: R-STRUCT-01
  typology: structuring
  severity: HIGH
  enabled: true
  window: 24h
  condition: "count_just_below_threshold_24h >= 3 and amount < 400_000_000"
  action_hint: FLAG
```

#### Inline validation
- Field-level error messages below each invalid input
- Condition syntax error shown with the problematic token highlighted
- Duplicate `rule_id` error on save attempt

#### Drawer actions
- **Save** — validates, writes, and marks file as "pending reload"
- **Test rule** — opens a sub-panel to evaluate the condition against a sample context (see below)
- **Cancel** — discards changes

### Rule test preview panel

Inside the drawer, a "Test" tab:
- Input: key-value pairs matching feature names (manually entered)
- "Run test" button
- Output: passes / fails badge + which part of the condition evaluated to true/false

### Version history panel

Available via the ⋯ menu → "View history":
- Timeline of past saves: timestamp, changed by, condition diff, enabled state
- "Restore this version" action

### Reload Rules flow

1. User clicks **Reload Rules**
2. Confirmation dialog: "Reload the active rule set? This will apply all saved changes immediately."
3. System calls `POST /api/v1/rules/reload`
4. On success: reload status banner turns green — "Rules reloaded successfully — version {rule_version}, {N} rules active"
5. On failure (invalid YAML / syntax error / duplicate ID): error banner — "Reload failed: {error.message}" — the previous valid rule set remains active (per TDD §4.2)
6. Reload events are written to Audit Log automatically

---

## API backing

| Action | Endpoint |
|--------|---------|
| Load rules | `GET /api/v1/rules` |
| Reload rule set | `POST /api/v1/rules/reload` |
| Create/edit rule | Future CRUD endpoints (or YAML file management) |

Auth: JWT required on all rule endpoints.

---

## States

### Loading
- Skeleton table rows (6 rows)

### Empty
- Empty state: "No rules defined yet — create your first rule to start detecting AML patterns" with Create Rule CTA

### Error states
- Inline validation errors per field in the form
- Reload failure: persistent banner (not toast) — stays visible until next successful reload
- Save conflict: "Another reload is in progress — please wait"

---

## Notes
- The reload operation is atomic: the engine only switches to the new rule set if the entire file is valid. A partial or broken file is rejected and the old set continues serving (REL-02).
- Use a drawer (not a full-page form) to preserve table context while editing — only switch to full-page if the DSL editor grows too complex for the drawer width.
- Enable/disable toggle in the table is a fast-action that does NOT require a full reload — it updates the in-memory state immediately and marks the rule set as "modified pending reload."
- Delete requires an `AlertDialog` confirmation: "Delete rule {rule_id}? This cannot be undone without a rule history restore."
- The 400,000,000 VND CTR threshold (Decision 11/2023/QĐ-TTg) is a locked constant — display it as a read-only informational note near the structuring rules.
