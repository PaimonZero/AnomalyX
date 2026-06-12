# AI Workflow Rules

## Approach

Build AnomalyX incrementally using a spec-driven workflow. The `documents/` folder provides source reports and run guidance; the six `context/` files translate that material plus current source code into implementation rules. Always implement against these specs and verify current code before changing behavior. Do not infer product behavior from generic AML expectations when repo docs define narrower prototype scope.

## Required Reading Before Implementation

Before making implementation or architectural decisions, read these files in order:

1. `context/project-overview.md`
2. `context/architecture.md`
3. `context/ui-context.md`
4. `context/code-standards.md`
5. `context/ai-workflow-rules.md`
6. `context/progress-tracker.md`

Then inspect relevant source files. Recalled docs can be stale; verify code before relying on exact paths, functions, or flags.

## Scoping Rules

- Work on one feature unit at a time.
- Prefer small, verifiable increments over broad speculative changes.
- Do not combine unrelated boundaries in one implementation step.
- Keep backend-only current state in mind; frontend work is future scope unless explicitly requested.
- Preserve self-contained default test behavior.
- Prefer existing factories/protocols over direct dependency wiring.
- Keep privacy invariants stronger than convenience shortcuts.
- If a requested change conflicts with PRD/TDD/current implementation, surface conflict before coding.

## When to Split Work

Split an implementation step if it combines any of these:

- API contract change plus persistence schema change plus frontend change.
- Rule DSL changes plus feature engineering changes plus ML model changes.
- Auth model changes plus business endpoint behavior changes.
- External infrastructure changes plus core service logic changes.
- Real ML artifact integration plus model training pipeline creation.
- LLM provider changes plus privacy/guardrail changes.
- PostgreSQL/Redis integration tests plus default unit test behavior changes.
- Behavior not clearly defined in context files.

If a change cannot be verified end to end quickly, scope is too broad. Split it.

## Handling Missing Requirements

- Do not invent product behavior not defined in `context/` or `documents/`.
- If requirement is ambiguous, update or add an open question in `context/progress-tracker.md` before implementation.
- If user answers an open question, update relevant context file and tracker.
- Use current source code as ground truth for implemented behavior; use documents for intended direction.
- If docs disagree with source, document actual state and ask before large rewrites.

## Protected Behaviors

Do not change these without explicit instruction and tests:

- Public/private route split: `/health` and `/metrics` public; prediction, batch, alerts, and rules protected.
- Uniform error envelope shape.
- Idempotency claim-before-work behavior.
- Background-only LLM explanation path.
- No raw payload/PII persistence invariant.
- Default pytest must remain infrastructure-free.
- Rule sandboxing through AST validation.
- PostgreSQL schema restrictions on stored data.

## Protected Files and Areas

Do not modify unless task requires it:

- `.env` real local secrets.
- Generated or external dependency files.
- Database schema without matching repository/service implications.
- `documents/` source reports, unless user asks to edit reports.
- `CLAUDE.md`, unless user asks to change project instructions.

## Implementation Checklist

1. Read required context files.
2. Inspect relevant source files with `Read`, `Glob`, or `Grep`.
3. Identify smallest safe change.
4. Update docs first if behavior/architecture/scope changes.
5. Implement code matching surrounding style.
6. Add or update tests for changed behavior.
7. Run focused tests first.
8. Run broader backend test command when practical: `python -m pytest tests -q` from `backend/`.
9. Update `context/progress-tracker.md` with meaningful implementation change.
10. Report exact files changed and test results.

## Verification Rules

- For backend logic changes, run focused pytest for touched area.
- For API route changes, run API tests or add new route tests.
- For config changes, run config tests and relevant `scripts/check_*.py` when external mode is involved.
- For persistence changes, test in-memory behavior by default and PostgreSQL path if infrastructure is available or user asks.
- For Redis idempotency changes, preserve in-memory tests and add Redis integration only as optional/skipped or script-based unless infrastructure is required.
- For LLM changes, stub provider calls in tests; do not require real OpenAI/Anthropic keys.
- If tests cannot be run, state why and list exact command user can run.

## Documentation Sync Rules

Update relevant context file whenever implementation changes:

- Product scope, user flows, feature list → `project-overview.md`
- System boundaries, storage, auth, invariants → `architecture.md`
- Frontend conventions or dashboard scope → `ui-context.md`
- Coding conventions or testing rules → `code-standards.md`
- Workflow/scoping/verification process → `ai-workflow-rules.md`
- Completed work, current phase, next steps, open questions → `progress-tracker.md`

`progress-tracker.md` must be updated after each meaningful implementation change. Documentation-only context generation, like initial creation of these files, also counts as meaningful project documentation work.

## Before Moving to Next Unit

1. Current unit works within defined scope.
2. No `architecture.md` invariant is violated.
3. Tests or explicit verification status are known.
4. `progress-tracker.md` reflects completed work and next steps.
5. Any changed architecture/scope/standards docs are synchronized.
6. User-facing summary reports failures and skipped checks honestly.

## External Services

- Do not call real LLM providers unless user explicitly configures/requests it.
- Do not require PostgreSQL/Redis/Supabase for default test suite.
- Use `docker compose up -d postgres redis` only when working on external-service mode or user requests full local infra.
- Use preflight scripts for external dependency validation rather than embedding checks into default tests.
- Never expose secret values in logs, docs, or summaries.

## Security and Privacy Workflow

- Treat AML data as sensitive even when synthetic.
- Keep identifiers masked or pseudonymous.
- Reject designs that persist raw transaction objects.
- Keep LLM context minimal, grounded, and masked.
- For auth changes, verify protected endpoints reject missing/invalid bearer token.
- For status/review actions, preserve audit metadata.

## Git Workflow

- Do not commit or push unless user asks.
- Before major edits, check current diff if needed; user may have uncommitted work.
- Do not revert user changes unless explicitly requested.
- Mention existing dirty files if relevant to final summary.

## Current Known Gaps To Respect

See `context/progress-tracker.md` Open Questions for the full list and resolution tracking. Guard rails for implementation work:

- Cold-start velocity/fan-out defaults in `_compute_features` are intentional; do not remove them without wiring Redis aggregates first.
- `_PAYSIM_THRESHOLD` is in PaySim synthetic units, not VND; do not align it to `CTR_THRESHOLD_VND` without retraining.
- `balance_diff_dest` is structurally zero at the API boundary; do not add logic that depends on it varying without sourcing real account state.
- Redis rolling aggregates not implemented; feature service uses constant cold-start defaults.
- React frontend not present.
- Explanation cache not fully wired.
- Real drift detection not fully wired.
- Docker Compose starts full stack but is not production-hardened.
