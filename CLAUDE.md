# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

AnomalyX is a backend-only FastAPI AML transaction anomaly detection prototype. A transaction is evaluated by a deterministic YAML rule engine and a probabilistic ML predictor; the decision engine reconciles both into final risk; flagged transactions create alerts; a background LLM explainer later annotates those alerts with grounded, masked explanations.

Current implementation is backend-only. React frontend, real ML training/model artifacts, Redis rolling aggregates, explanation cache, and real drift detection remain gaps. Docker Compose provides PostgreSQL + Redis infrastructure only, not a full production stack.

## Commands

Run backend commands from `backend/` unless noted.

```bash
# Install dependencies (from repo root)
python -m pip install -r backend/requirements.txt

# Start local infra (from repo root)
docker compose up -d postgres redis

# Run API (Swagger UI at http://localhost:8000/docs)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Tests
python -m pytest tests -q
python -m pytest tests/test_prediction_api.py -q
python -m pytest tests/test_prediction_api.py::test_predict_rejects_invalid_payload -q
python -m pytest tests/test_postgres_config.py -q

# Preflight checks
python scripts/check_config.py
python scripts/check_postgres.py   # active only when ALERT_REPOSITORY=postgres
python scripts/check_supabase.py   # active only when ALERT_REPOSITORY=supabase
python scripts/check_redis.py      # active only when IDEMPOTENCY_STORE=redis
```

There is no linter/formatter configured. The `.env` file lives at repo root, not in `backend/`; copy from `.env.example`.

Quick local mode without external services:

```env
ALERT_REPOSITORY=in_memory
IDEMPOTENCY_STORE=in_memory
AUTH_TOKEN=dev-service-token
JWT_SECRET_KEY=dev-jwt-secret
MOCK_ML_ENABLED=true
```

PostgreSQL/Redis mode:

```env
ALERT_REPOSITORY=postgres
DATABASE_URL=postgresql+psycopg://anomalyx_user:anomalyx_password@localhost:5432/anomalyx
IDEMPOTENCY_STORE=redis
REDIS_URL=redis://localhost:6379/0
AUTH_TOKEN=dev-service-token
JWT_SECRET_KEY=dev-jwt-secret
MOCK_ML_ENABLED=true
```

## Architecture

Layered FastAPI service under `backend/app/`. Main request flow for `POST /api/v1/predict` lives in `services/prediction_service.py`:

1. Idempotency claim (`services/idempotency_service.py`) — defaults key to `transaction_id`; returns cached response for repeats or waits if another request is processing.
2. Rule engine (`rules/engine.py`) — evaluates `configs/rules.yaml` conditions over a feature context.
3. ML predictor (`ml/`) — returns `risk_score`, `model_version`, and `top_features`. Mock predictor is current working mode.
4. Decision engine (`core/decision.py`) — rule severity overrides ML score; otherwise thresholds decide `LOW`/`MEDIUM`/`HIGH` and `is_flagged`.
5. Alert/audit persistence (`services/alert_service.py`, `repositories/`) — flagged transactions create alerts; every prediction attempts an audit log write.
6. LLM explanation (`llm/`) — flagged alerts enqueue a FastAPI `BackgroundTask`; prompt context is masked and grounded; failures fall back to deterministic template text.

## Key conventions

- Routing/auth: `/health` and `/metrics` are public; `/predict`, `/batch-score`, `/alerts`, and `/rules` require `Authorization: Bearer <AUTH_TOKEN>` via `api/dependencies/auth.py`.
- Error handling: `app/core/errors.py` and `app/main.py` normalize validation/domain errors into the uniform `{error:{code,message,details}}` envelope.
- Config: `core/config.py` builds cached `Settings` from env plus root `.env`; call `reset_settings_cache()` in tests after env changes. `AUTH_TOKEN` and `JWT_SECRET_KEY` are required. PostgreSQL creds are required only for `ALERT_REPOSITORY=postgres`; Supabase creds only for `ALERT_REPOSITORY=supabase`.
- Backend factories are env-switched and cached:
  - `repositories/factory.py`: `ALERT_REPOSITORY=in_memory|postgres|supabase`; PostgreSQL is primary persistence, Supabase is optional legacy.
  - `repositories/idempotency_factory.py`: `IDEMPOTENCY_STORE=in_memory|redis`.
  - `ml/factory.py`: `MOCK_ML_ENABLED` selects deterministic `MockPredictor` (`mock-ml-v1`).
- Rule DSL is sandboxed in `rules/engine.py` using AST validation. When adding rule inputs, update both `ALLOWED_CONTEXT_NAMES` and `features/service.py`.
- LLM guardrails: `llm/secure_data_wrapper.py` masks identifiers before prompting; `llm/explainer.py` rejects unsupported rule IDs/features or PII-looking output. Persisted `explanation_source` is `llm` or `template`.
- Metrics: `core/metrics.py` defines Prometheus metrics; `core/middleware.py` attaches request context and records request metrics.

## Data layer

Primary PostgreSQL schema: `backend/db/schema.sql`.

Active tables:

- `alerts`
- `review_labels`
- `prediction_logs`

Schema-ready but not fully wired:

- `feature_snapshots`
- `rule_versions`
- `model_registry`

Repository adapters:

- `app/repositories/alert_repository.py` — protocol + in-memory implementation used by tests/local quick mode.
- `app/repositories/postgres_alert_repository.py` — SQLAlchemy + psycopg PostgreSQL implementation.
- `app/repositories/supabase_alert_repository.py` — optional legacy Supabase REST adapter.

Stored records must remain limited to transaction IDs, prediction outputs, derived feature/rule evidence, alert review metadata, explanations, and timestamps. Do not add raw transaction payload or raw PII storage.

## Tests

`tests/conftest.py` provides autouse fixtures that:

- set auth/config defaults,
- override FastAPI auth dependency,
- force in-memory alert/idempotency repositories,
- stub OpenAI explainer calls.

Follow that pattern for API/service tests so default pytest never needs PostgreSQL, Redis, Supabase, or OpenAI.

Integration checks for external services belong in scripts or explicitly skipped tests; default `python -m pytest tests -q` should stay self-contained.

## Application Building Context

Read the following files in order before implementing
or making any architectural decision:

1. `context/project-overview.md` — product definition,
   goals, features, and scope
2. `context/architecture.md` — system structure,
   boundaries, storage model, and invariants
3. `context/ui-context.md` — theme, colors, typography,
   and component conventions
4. `context/code-standards.md` — implementation rules
   and conventions
5. `context/ai-workflow-rules.md` — development workflow,
   scoping rules, and delivery approach
6. `context/progress-tracker.md` — current phase,
   completed work, open questions, and next steps

Update `context/progress-tracker.md` after each
meaningful implementation change.

If implementation changes the architecture, scope, or
standards documented in the context files, update the
relevant file before continuing.
