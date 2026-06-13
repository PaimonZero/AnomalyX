# Optional Geo/Device Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align docs and source with PRD/TDD by adding backward-compatible optional geo/device inputs and documenting remaining prototype gaps.

**Architecture:** Keep transaction geo/device evidence optional. Missing fields must produce neutral feature values so existing clients keep working and no fake risk is introduced. Patch stale roadmap/run/context docs to reflect current bearer-auth/PostgreSQL/backend-only state.

**Tech Stack:** FastAPI, Pydantic, YAML rule engine, pytest, Markdown docs.

---

### Task 1: Add optional geo/device fields and neutral features

**Files:**
- Modify: `backend/app/schemas/prediction.py`
- Modify: `backend/app/features/service.py`
- Modify: `backend/app/rules/engine.py`
- Test: `backend/tests/test_rule_engine.py`

- [ ] Step 1: Add failing tests for backwards compatibility and optional geo/device rule behavior.
- [ ] Step 2: Run focused test and confirm failure.
- [ ] Step 3: Add optional fields to `TransactionRequest`.
- [ ] Step 4: Add neutral geo/device features when fields missing.
- [ ] Step 5: Add feature names to rule allowlist.
- [ ] Step 6: Run focused tests and confirm pass.

### Task 2: Add safe R-GEO-01 rule

**Files:**
- Modify: `configs/rules.yaml`
- Test: `backend/tests/test_rule_engine.py`

- [ ] Step 1: Add test asserting missing geo/device fields do not trigger geo rule.
- [ ] Step 2: Add `R-GEO-01` with condition requiring optional evidence.
- [ ] Step 3: Run rule tests.

### Task 3: Align docs

**Files:**
- Modify: `documents/Backend_Run_Guide.md`
- Modify: `documents/Remaining_Project_Roadmap.md`
- Modify: `context/project-overview.md`
- Modify: `context/architecture.md`
- Modify: `context/code-standards.md`
- Modify: `context/progress-tracker.md`

- [x] Step 1: Confirm bearer token language: `Authorization: Bearer <AUTH_TOKEN>`.
- [ ] Step 2: Replace stale Supabase-primary language with PostgreSQL-primary/Supabase-legacy language.
- [ ] Step 3: Document optional geo/device fields and limitation without historical profile/Redis aggregates.
- [ ] Step 4: Update progress tracker with completed work and remaining Report2 gaps.

### Task 4: Verify

**Files:**
- Use tests only.

- [ ] Step 1: Run focused tests: `python -m pytest tests/test_rule_engine.py tests/test_prediction_api.py -q` from `backend/`.
- [ ] Step 2: Run full tests when practical: `python -m pytest tests -q` from `backend/`.
- [ ] Step 3: Report Report2 changes needed clearly.
