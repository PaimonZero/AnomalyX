# Rule Engine Screen Spec

## Purpose
The Rule Engine screen provides full management of AML detection rules — individual rule CRUD, ruleset-level file uploads, version history, version switching (rollback/promote), and hot-reload — fulfilling UC-05 (Update rule config) from the PRD.

## Primary users
- ML/Risk Engineer (primary)
- Admin

## Goals
- Manage individual rules as first-class operational assets (create, edit, enable/disable, delete)
- Upload a new YAML rule file to replace or extend the active configuration
- Inspect the full version history of the ruleset and understand what changed between versions
- Promote (rollback to) any previous version as the new active set
- Execute hot-reload safely with visible validation feedback before activation
- Allow testing a rule condition against a sample feature context before deploying

---

## Conceptual model (read this first)

The Rule Engine works at two distinct levels. The spec covers both:

| Level | What it is | Where it lives |
|-------|-----------|---------------|
| **Ruleset version** | A full snapshot of `configs/rules.yaml` — all rules together, versioned atomically | `rule_versions` table in PostgreSQL |
| **Individual rule** | One rule entry within the active ruleset — editable, togglable, deletable | Derived from the active ruleset version in memory |

**Active vs. staged:**
- The **active version** is the ruleset currently loaded in memory and used by the Decision Engine for scoring.
- A **staged version** is one that has been saved (via form edits or file upload) but not yet reloaded. It exists in the database but is not yet serving.
- Reload (`POST /api/v1/rules/reload`) atomically swaps staged → active. A failed reload leaves the active version unchanged.

---

## Layout

The page has two top-level tabs:

```
[ Rules ]   [ Versions ]
```

- **Rules tab** (default): individual rule table + create/edit drawer
- **Versions tab**: full ruleset version history, upload, promote/rollback

Both tabs share the top action row and the page header.

### Page header
- Title "Rule Engine"
- Subtitle: "Active: v{rule_version} · {N} rules · Last reloaded {relative time}"
- Right: **Upload Rule File** button (secondary) + **Reload Rules** button (primary with ↺ icon)

---

## Tab 1: Rules

### Top filter / search row

| Filter | Type | Options |
|--------|------|---------|
| Search | Text | Matches `rule_id` or `typology` (partial) |
| Severity | Multi-select | CRITICAL · HIGH · MEDIUM · MINOR |
| Enabled | Select | All · Enabled only · Disabled only |
| Typology | Multi-select | structuring · smurfing · rapid_movement · layering · velocity_anomaly · geo_device_anomaly |
| **Create Rule** | Button (primary) | Opens create drawer |

### Rules table

Reflects the **active** ruleset. A "Modified — reload pending" banner appears above the table if staged edits exist that have not been reloaded.

| Column | Field | Display |
|--------|-------|---------|
| Rule ID | `rule_id` | Monospace badge (e.g. `R-STRUCT-01`) |
| Typology | `typology` | Human-readable label |
| Severity | `severity` | Colored badge — CRITICAL=red, HIGH=orange, MEDIUM=amber, MINOR=muted |
| Condition | `condition` (truncated) | Monospace code, 60 chars max + "…"; full on hover tooltip |
| Window | `window` | Duration chip (e.g. `24h`) |
| Action hint | `action_hint` | `FLAG` · `BLOCK` · `ALLOW` chip |
| Enabled | `enabled` | Inline toggle switch — fast-action, marks set as pending reload |
| Updated | `updated_at` | Relative + full ISO timestamp tooltip |
| Actions | — | ⋯ menu: Edit · Duplicate · Test · Delete · View rule history |

### Initial rule set (always seeded — from TDD §4.3)

| Rule ID | Typology | Severity | Informal condition |
|---------|----------|----------|--------------------|
| `R-STRUCT-01` | structuring | HIGH | ≥3 txns just below 400M VND within 24h |
| `R-SMURF-01` | smurfing | HIGH | distinct_receivers_1h ≥ N and sum_amount_1h ≥ X |
| `R-RAPID-01` | rapid_movement | HIGH | in→out within 60 min, repeated ≥ k times |
| `R-LAYER-01` | layering | MEDIUM | chain_depth ≥ 3 with near-equal amounts |
| `R-VELO-01` | velocity_anomaly | MEDIUM | velocity_vs_baseline_ratio > 10 |
| `R-GEO-01` | geo_device_anomaly | MEDIUM | new device or geo anomaly (partial — requires Redis history) |

---

### Rule Create / Edit Drawer

Opens from "Create Rule" button or "Edit" in the ⋯ menu. Slides in from the right; does not replace the table view.

#### Drawer tabs: [ Form ] [ YAML Preview ] [ Test ]

**Form tab:**

| Field | Input type | Validation |
|-------|-----------|-----------|
| Rule ID | Text (monospace) | Required; unique in active set; pattern `[A-Z]+-[A-Z]+-[0-9]{2}` |
| Typology | Select | Required; from enum values |
| Severity | Select | Required; CRITICAL · HIGH · MEDIUM · MINOR |
| Condition | Textarea (monospace, DSL) | Required; validated against feature whitelist |
| Window | Text | Optional duration string — `24h`, `1h`, `7d` |
| Action hint | Select | FLAG · BLOCK · ALLOW |
| Enabled | Switch | Default true |

**DSL feature name whitelist** (inline collapsible helper below the condition textarea):

| Group | Feature names |
|-------|--------------|
| Transaction | `log_amount`, `hour_of_day`, `is_round_amount`, `amount_to_threshold_ratio` |
| Velocity | `tx_count_1h`, `tx_count_24h`, `tx_count_7d`, `sum_amount_1h`, `sum_amount_24h`, `std_amount` |
| Counterparty | `distinct_receivers_1h`, `distinct_receivers_24h`, `fan_out`, `fan_in` |
| Behavioural | `amount_zscore_vs_user`, `velocity_vs_baseline_ratio` |
| Sequence | `rapid_inout_flag`, `chain_depth` |
| Structuring | `count_just_below_threshold_24h`, `sum_just_below` |

Allowed operators: `and`, `or`, `not`, `>`, `>=`, `<`, `<=`, `==`, `!=`, numeric literals, parentheses.
Sandbox note: arbitrary code, imports, function calls, and string operations are not permitted.

**YAML Preview tab:**

Shows the rule as it will appear in `configs/rules.yaml`. Read-only; updates live as the form fields change:

```yaml
- id: R-STRUCT-01
  typology: structuring
  severity: HIGH
  enabled: true
  window: 24h
  condition: "count_just_below_threshold_24h >= 3 and amount < 400_000_000"
  action_hint: FLAG
```

**Test tab:**

Evaluate the current condition against a manually provided feature context before saving.

- Input section: key-value form — each row is a feature name (select from whitelist) + numeric value
- "Run test" button
- Output:
  - **PASSES** (green) or **FAILS** (muted) badge
  - Condition evaluation trace: each sub-expression highlighted true/false
  - Example: `count_just_below_threshold_24h >= 3` → `4 >= 3` → **true**

**Drawer footer actions:**
- **Save** — validates, stages the change, marks the set as "pending reload". Shows inline error if validation fails.
- **Cancel** — discards unsaved changes without prompting if the form is clean; confirms if dirty.

---

### Per-rule version history (from ⋯ menu → "View rule history")

Shows a timeline of changes to a single rule across all ruleset versions:

| Column | Detail |
|--------|--------|
| Version | `v3`, `v2`, `v1` — ruleset version where this rule changed |
| Changed at | ISO timestamp |
| Changed by | `actor_id` (mono) |
| Field changed | `condition`, `severity`, `enabled`, `window` |
| Diff | Side-by-side or inline diff of the condition string |

**Restore this rule from version** — stages the single rule back to its state at that version (does not affect other rules). Requires reload to activate.

---

## Tab 2: Versions

### Purpose of this tab
The Versions tab manages the full ruleset as a unit: upload a new YAML, inspect past snapshots, compare versions, and promote any past version to active.

---

### Versions timeline (main content)

A vertical timeline — most recent version at top.

Each version card shows:

| Field | Display |
|-------|---------|
| Version tag | `v4` (current active — highlighted with "ACTIVE" chip) |
| Created at | ISO timestamp + relative |
| Created by | `actor_id` + role badge |
| Source | `form_edit` · `file_upload` · `rollback` |
| Summary | "6 rules · 2 changed · 1 added" (diff from previous) |
| Rule diff count | N rules added / M rules changed / K rules removed |
| Status | `active` · `staged` · `superseded` |
| Actions | **View** · **Compare** · **Promote to active** |

**Status meanings:**
- `active` — currently loaded by the Decision Engine
- `staged` — saved but not yet reloaded (most recent pending version)
- `superseded` — older version, replaced by a newer one

**Promote to active flow:**
1. User clicks **Promote to active** on any `superseded` or `staged` version
2. Confirmation dialog: "Promote v{N} to active? This will reload the rule engine with this version's configuration."
3. On confirm: system calls `POST /api/v1/rules/reload` with the target version reference
4. On success: version card updates to `active`; previous active card downgrades to `superseded`; reload banner confirms
5. On failure: error banner; current active version unchanged

---

### Version diff viewer

Opens on **Compare** or when viewing a version.

Two-panel diff:
- Left panel: selected version's full YAML
- Right panel: the active version's full YAML (or any other selected version)
- Line-level diff highlighting:
  - Green lines: added in the right version
  - Red lines: removed from the left version
  - Unchanged lines: muted

Rule-level change summary above the diff:
```
v2 → v3
+ R-VELO-02 added (velocity_anomaly, MEDIUM)
~ R-STRUCT-01 condition changed
~ R-GEO-01 severity changed: MEDIUM → HIGH
```

---

### Upload Rule File section (top of Versions tab, or via modal)

Allows uploading a complete new `rules.yaml` to replace the staged version. Triggered by the **Upload Rule File** button in the page header.

#### Upload flow

**Step 1 — File input:**
- Drag-and-drop zone: accepts `.yaml` / `.yml` only
- Or: "Paste YAML" textarea tab
- File size limit: displayed (e.g. 512 KB max)
- "Clear" button to reset

**Step 2 — Validate (automatic on upload):**
The system runs validation before allowing staging:

| Check | Pass condition |
|-------|---------------|
| YAML syntax | Parses without error |
| Schema valid | `version`, `rules` keys present |
| All `rule_id` unique | No duplicates within the file |
| Known feature names | All condition variables are in the feature whitelist |
| Parseable conditions | All DSL conditions evaluate syntactically |
| Severity values | All severities are in CRITICAL · HIGH · MEDIUM · MINOR |

Validation results display:
- ✓ N rules found
- ✓ All rule IDs unique
- ✗ Line 14: unknown feature name `foo_bar` — **blocks staging**
- ⚠ R-GEO-01: geo/device features are partially supported (warning, does not block)

**Step 3 — Diff preview (if validation passes):**
Shows what will change vs. the current active version:
```
+ R-NEW-01 will be added (structuring, HIGH)
~ R-STRUCT-01 condition will change
  before: count_just_below_threshold_24h >= 3 and amount < 400_000_000
  after:  count_just_below_threshold_24h >= 2 and amount < 400_000_000
- R-LAYER-01 will be removed
```

**Step 4 — Stage:**
- **Stage this version** button (enabled only when validation passes)
- On stage: new entry appears in the Versions timeline as `staged`; header subtitle updates to "Staged changes pending reload"
- Staging does NOT activate — the Decision Engine continues using the current `active` version

**Step 5 — Reload (separate explicit action):**
- **Reload Rules** button in the page header triggers reload of the staged version
- User must explicitly reload — staging and reloading are two separate steps so engineers can review before activating

#### Upload error states

| Error | Message |
|-------|---------|
| Wrong file type | "Only .yaml / .yml files are accepted" |
| YAML parse error | "Invalid YAML syntax at line {N}: {message}" |
| Duplicate rule IDs | "Duplicate rule_id found: R-STRUCT-01 (lines 4 and 22)" |
| Unknown feature | "Unknown feature name '{name}' in rule {rule_id}. Check the feature whitelist." |
| File too large | "File exceeds 512 KB limit" |

---

### Reload Rules flow (from either tab)

1. User clicks **Reload Rules** in the page header
2. If no staged version exists: "No pending changes — the active version is already up to date."
3. If staged version exists: confirmation dialog
   - Title: "Reload rule engine?"
   - Body: shows staged version summary ("v4 — 7 rules, 1 change from active")
   - **Reload** (primary) + **Cancel**
4. System calls `POST /api/v1/rules/reload`
5. On success:
   - Green banner: "Rules reloaded — v{N} now active · {K} rules · reloaded at {timestamp}"
   - Versions timeline updates: staged → active, previous active → superseded
   - Header subtitle updates
   - Reload event written to Audit Log automatically
6. On failure (invalid YAML / syntax error / duplicate rule_id):
   - Persistent error banner (not toast — stays until dismissed or next successful reload): "Reload failed: {error.code} — {error.message}. Previous version v{N} remains active."
   - Failed version remains `staged` (not discarded) so engineer can fix and retry
   - Error details are expandable: show which rule and which line caused the failure

---

## API backing

| Action | Endpoint | Notes |
|--------|---------|-------|
| Load active rules | `GET /api/v1/rules` | Returns current active ruleset |
| Reload staged → active | `POST /api/v1/rules/reload` | Atomic; rejects invalid files |
| Load version history | Future: `GET /api/v1/rules/versions` | Reads from `rule_versions` table |
| Get specific version | Future: `GET /api/v1/rules/versions/{version_id}` | Full YAML snapshot |
| Promote version | Future: `POST /api/v1/rules/versions/{version_id}/promote` | Stages that version then reloads |

Auth: JWT required on all rule endpoints.

---

## States

### Loading (Rules tab)
- Skeleton table rows (6 rows)

### Loading (Versions tab)
- Skeleton version cards (3 cards)

### Empty (Rules tab)
- "No rules in the active set — upload a rule file or create your first rule"

### Empty (Versions tab)
- "No version history yet — the rule set has not been modified since initial load"

### Pending reload banner
Appears at the top of both tabs when staged ≠ active:
- "⚠ Unsaved changes — {N} rule(s) have been modified. Reload to activate."
- **Reload now** shortcut button in the banner

### Reload success banner
- Green, auto-dismisses after 8 seconds
- "✓ Rules reloaded — v{N} is now active · {K} rules · {timestamp}"

### Reload failure banner
- Red, persistent (manual dismiss)
- "✗ Reload failed — {error.message}. v{prev} remains active."
- **View error details** expands to show the problematic rule and line

---

## Notes

- Staging and reloading are **explicitly separated** — uploading or saving a rule does not activate it. This gives the engineer a review window.
- The atomicity guarantee (from TDD §4.2) means a broken file never partially activates. The active version is always a valid, fully-validated snapshot.
- Enable/disable toggle on a rule in the table is a fast-action that stages the change immediately and shows the pending reload banner — it does not reload automatically.
- Delete requires an `AlertDialog` confirmation: "Delete rule {rule_id}? This stages the deletion. Reload to apply."
- The 400,000,000 VND CTR threshold is a locked regulatory constant (Decision 11/2023/QĐ-TTg) — show it as a read-only note near structuring rules and in the Upload helper text.
- The Versions tab is the authoritative view of what was active at any point in time — it supports the Audit Log's rule change events.
- R-GEO-01 partial implementation: always show a `⚠ partial` chip next to this rule's row explaining "Geo/device anomaly detection requires Redis per-user history — currently defaults to false."
