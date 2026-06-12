# Code Standards

## General

- Keep backend layered: routes validate/dispatch, services orchestrate, core holds cross-cutting logic, repositories persist.
- Fix root causes; do not paper over failing tests or weaken validation.
- Match surrounding naming, imports, and comment density.
- Prefer explicit, small functions over large mixed-concern blocks.
- Keep public API contracts stable unless documents and tests are updated first.
- Do not introduce network or external-service requirements into default unit/API tests.
- Do not store raw transaction payloads or raw PII.
- Do not print secrets, API keys, bearer tokens, database passwords, or Supabase service keys.

## Python

- Use Python 3.11+ syntax already present in codebase, including `|` unions and `StrEnum`.
- Use Pydantic models for API request/response boundaries.
- Use dataclasses for small internal immutable value objects when appropriate.
- Type annotate new functions and class attributes where practical.
- Raise domain/config-specific errors where code already defines them (`ConfigError`, `RuleEngineError`, etc.).
- Avoid broad `except Exception` unless failure must be isolated and logged, such as audit log writes or batch item failure handling.
- When catching broad exceptions, log with useful context and do not leak sensitive payloads.
- Keep imports grouped like existing files: `__future__`, standard library, third-party, app imports.

## FastAPI

- Put API endpoints under `backend/app/api/v1/routes/` and include them via `backend/app/api/v1/router.py`.
- Use `response_model` on routes.
- Keep route handlers thin; call services for business logic.
- Protected business routes must use `require_api_auth` through router dependencies.
- `/health` and `/metrics` are the only public endpoints unless context docs explicitly change.
- Use FastAPI `BackgroundTasks` for non-blocking explanation work.
- Preserve uniform error envelope `{ "error": { "code", "message", "details" } }` for validation/domain errors.
- Do not add blocking external LLM calls to synchronous request path.

## Configuration

- Load runtime config through `get_settings()` from `backend/app/core/config.py`.
- Add new environment variables to `Settings`, parsing helpers, validation, `.env.example`, and relevant docs.
- Call `reset_settings_cache()` in tests after changing environment variables.
- Keep repo-root `.env` behavior; do not move `.env` into `backend/`.
- Required secrets must remain env-based and excluded from version control.
- New repository or external provider modes must validate only when selected.

## Schemas and API Contracts

- Add request/response fields in `backend/app/schemas/` first.
- Keep prediction response fields compatible: `transaction_id`, `risk_score`, `risk_level`, `is_flagged`, `model_version`, `triggered_rules`, `top_features`, `explanation`, `explanation_source`, `alert_id`.
- Use enums for closed sets (`RiskLevel`, `RuleSeverity`, transaction channel, alert status).
- Batch APIs should isolate per-item failures and continue processing remaining valid items.
- Keep error messages useful but not payload-leaking.

## Rule Engine

- Rule conditions must stay declarative YAML over whitelisted context names.
- Never replace sandboxed AST evaluation with Python `eval`, `exec`, or dynamic imports.
- When adding a rule input, update both:
  - `backend/app/rules/engine.py` `ALLOWED_CONTEXT_NAMES`
  - `backend/app/features/service.py` `FeatureService.compute`
- Rule reload must parse, validate, compile, and then atomically replace active engine only on success.
- Duplicate rule IDs must remain invalid.
- Invalid rule config must keep previous valid config active.
- Add tests for new DSL operators, feature names, or rule failure modes.

## ML Integration

- New predictors must implement `ModelPredictor` contract from `backend/app/ml/predictor.py`.
- Predictor output must include `risk_score` in `[0, 1]`, `model_version`, and `top_features`.
- Real model adapter should load artifacts once, not per request.
- Keep `MOCK_ML_ENABLED=true` path working for tests and local demos.
- Do not introduce GPU-only inference requirements.
- Do not let ML predictor decide final `risk_level`; final decision stays in `DecisionEngine`.
- Calibration thresholds belong in config/model metadata; tests must cover threshold behavior.

## Decision Logic

- `CRITICAL` rule severity takes precedence over all ML scores and flags as `CRITICAL`.
- `HIGH` rule severity takes precedence over ML score and flags as `HIGH`.
- ML score greater than or equal to `RISK_THRESHOLD_FLAG` flags as `HIGH` only when no higher rule override exists.
- ML score greater than or equal to `RISK_THRESHOLD_MEDIUM` but below flag threshold produces `MEDIUM` and does not create alert.
- Update decision tests before/with any threshold or precedence changes.

## Repositories and Storage

- Use repository protocols/factories; do not couple services directly to SQLAlchemy, Supabase, Redis, or in-memory implementations.
- PostgreSQL schema lives in `backend/db/schema.sql`; update schema and repository together.
- Stored records must remain limited to transaction IDs, risk outputs, derived evidence, review metadata, explanations, and timestamps.
- Raw transaction request objects must not be persisted.
- Prediction audit writes must not fail the whole prediction when persistence is temporarily unavailable.
- In-memory repositories must remain deterministic and safe for tests.
- Redis idempotency must use atomic claim semantics (`SET NX`-style behavior) to prevent duplicate side effects.

## LLM and Privacy

- Send only masked, grounded context to LLM providers.
- Never send raw transaction payloads, raw sender/receiver identifiers, secrets, or unsupported historical claims.
- LLM output must be checked for unsupported rule IDs/features or PII-looking content before persistence.
- On LLM provider failure, timeout, unsupported output, or missing key, use template fallback.
- Persist `explanation_source` as `llm` or `template` only.
- Explanations must reference supplied rules/features only.

## Logging and Metrics

- Use existing logging setup; include request/transaction identifiers where safe.
- Do not log request bodies or raw payloads.
- Add Prometheus metrics in `backend/app/core/metrics.py` and record them from service/middleware boundaries.
- Metrics labels must avoid unbounded cardinality; do not label by transaction ID, alert ID, sender ID, receiver ID, or raw exception messages.
- Health/readiness checks should report dependency status without exposing secrets.

## Testing

- Default command: run from `backend/` with `python -m pytest tests -q`.
- Follow `tests/conftest.py` pattern: default env values, dependency override, in-memory repositories, stub LLM calls.
- Unit tests cover core decision, rules, features, config, repositories, and services.
- API tests use FastAPI test client and must not require external infrastructure.
- External service checks belong in scripts or explicitly skipped integration tests.
- Add regression tests for bug fixes, especially idempotency, auth, persistence, and error envelopes.
- Keep tests deterministic; avoid sleeps unless testing concurrency behavior and no better synchronization exists.

## File Organization

- `backend/app/api/v1/routes/` — endpoint functions only.
- `backend/app/schemas/` — Pydantic models and enums.
- `backend/app/services/` — orchestration and use-case services.
- `backend/app/core/` — config, decision, errors, middleware, logging, metrics.
- `backend/app/features/` — feature engineering and feature context construction.
- `backend/app/rules/` — rule config loading/evaluation/reload.
- `backend/app/ml/` — predictor interfaces, factories, mock/real implementations.
- `backend/app/llm/` — masking, prompt construction, provider calls, fallback.
- `backend/app/repositories/` — persistence protocols and adapters.
- `backend/tests/` — pytest suite.
- `backend/scripts/` — manual/operator checks.
- `backend/db/` — SQL schema.
- `documents/` — reports and guides.
- `context/` — working context specs; update after meaningful changes.

## Documentation

- Update `context/progress-tracker.md` after each meaningful implementation change.
- If a change affects architecture, update `context/architecture.md` before or with code.
- If a change affects product scope/features, update `context/project-overview.md`.
- If a change affects frontend conventions, update `context/ui-context.md`.
- If a change affects engineering rules, update `context/code-standards.md` or `context/ai-workflow-rules.md`.
- Keep `documents/` as source reports/guides; do not rewrite unless requested.
