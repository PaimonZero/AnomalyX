# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

AnomalyX is an AML transaction anomaly detection prototype with a FastAPI backend and a React/Vite frontend for the core demo workflows. A transaction is evaluated by a deterministic YAML rule engine and a probabilistic ML predictor; the decision engine reconciles both into final risk; flagged transactions create alerts; a background LLM explainer later annotates those alerts with grounded, masked explanations.

Current implementation includes the backend pipeline, PostgreSQL/Redis infrastructure, optional real XGBoost runtime inference (`XGBPredictor` in `backend/app/ml/xgb_predictor.py`), and frontend pages for Alerts, API Testing, Predict Batch, and Monitoring. Redis rolling aggregates, explanation cache, real drift detection, and production deployment hardening remain gaps. Docker Compose can start the API + PostgreSQL + Redis stack; the frontend runs separately for local development.

## Commands

### Backend (run from `backend/` unless noted)

```bash
# Install dependencies (from repo root)
python -m pip install -r backend/requirements.txt

# Start local infra (from repo root)
docker compose up -d postgres redis

# Full Docker stack: api + postgres + redis (from repo root)
docker compose up --build -d

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

### Frontend (run from `frontend/`)

```bash
npm install
npm run dev        # Vite dev server with /api proxy to 127.0.0.1:8000
npm run build      # tsc + vite build
npm run lint       # ESLint
npm run test:monitoring  # Prometheus parser tests (Node --experimental-strip-types)
```

Frontend expects `VITE_API_BASE_URL=http://localhost:8000/api/v1` (or relies on the Vite proxy). Set `VITE_API_TOKEN` to match backend `AUTH_TOKEN` and `VITE_REVIEWER_ID` for review actions.

### ML pipeline (run from `ml/`)

```bash
make pipeline   # regenerate training artifacts from raw PaySim CSV
```

ML artifacts (`xgb_aml_v1.json`, `lgb_aml_v1.txt`, `rf_baseline.pkl`) are tracked via Git LFS. Raw PaySim CSV (~493 MB) is excluded from version control. Run `make pipeline` inside `ml/` to regenerate locally.

## Quick-start .env configurations

The `.env` file lives at repo root, not in `backend/`; copy from `.env.example`.

Quick local mode without external services:

```env
ALERT_REPOSITORY=in_memory
IDEMPOTENCY_STORE=in_memory
AUTH_TOKEN=<AUTH_TOKEN>
JWT_SECRET_KEY=<JWT_SECRET_KEY>
MOCK_ML_ENABLED=true
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174
```

PostgreSQL/Redis mode:

```env
ALERT_REPOSITORY=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=anomalyx
POSTGRES_USER=anomalyx_user
POSTGRES_PASSWORD=<POSTGRES_PASSWORD>
POSTGRES_SSLMODE=disable
IDEMPOTENCY_STORE=redis
REDIS_URL=redis://localhost:6379/0
AUTH_TOKEN=<AUTH_TOKEN>
JWT_SECRET_KEY=<JWT_SECRET_KEY>
MOCK_ML_ENABLED=true
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174
```

To use real XGBoost: set `MOCK_ML_ENABLED=false`, ensure `MODEL_PATH` and `MODEL_CONFIG_PATH` point to valid artifacts, then restart.

## Architecture

### Backend (FastAPI)

Layered service under `backend/app/`. Main request flow for `POST /api/v1/predict` lives in `services/prediction_service.py`:

1. Idempotency claim (`services/idempotency_service.py`) — defaults key to `transaction_id`; returns cached response for repeats or waits if another request is processing.
2. Rule engine (`rules/engine.py`) — evaluates `configs/rules.yaml` conditions over a feature context.
3. ML predictor (`ml/`) — returns `risk_score`, `model_version`, and `top_features`. Two implementations:
   - `MockPredictor` (`ml/mock_predictor.py`) — deterministic, selected when `MOCK_ML_ENABLED=true`.
   - `XGBPredictor` (`ml/xgb_predictor.py`) — real XGBoost inference mapping `TransactionRequest` to 26 PaySim features, returning SHAP top-5. Selected when `MOCK_ML_ENABLED=false`.
4. Decision engine (`core/decision.py`) — rule severity overrides ML score; otherwise thresholds decide `LOW`/`MEDIUM`/`HIGH` and `is_flagged`.
5. Alert/audit persistence (`services/alert_service.py`, `repositories/`) — flagged transactions create alerts; every prediction attempts an audit log write.
6. LLM explanation (`llm/`) — flagged alerts enqueue a FastAPI `BackgroundTask`; prompt context is masked and grounded; failures fall back to deterministic template text.

`FeatureService.compute` (`features/service.py`) builds the feature context for rules and ML. Velocity/fan-out features (`tx_count_sender`, `fan_out_orig`, etc.) currently use cold-start constant defaults — these suppress scores for high-velocity patterns until Redis rolling aggregates are wired.

### Frontend (React + Vite + TypeScript)

Stack: React 19, TypeScript, Vite 7, Tailwind CSS 4, TanStack Query v5, React Router v7, Lucide React icons.

Feature-first structure under `frontend/src/`:

- `app/` — bootstrap, router, global providers (auth token, theme, header actions)
- `layouts/` — app shell with fixed sidebar + header + scrollable content
- `features/alerts/` — alert list/detail/status-update pages, hooks, and API calls against real FastAPI endpoints
- `features/api-testing/` — request builder/response viewer for all nine backend endpoints
- `features/batch-scoring/` — JSON file/paste editor → `POST /api/v1/batch-score` → sortable results table
- `features/monitoring/` — health + Prometheus metrics display with Prometheus text parser
- `shared/api/` — typed API client with normalized error handling
- `shared/types/` — TypeScript contracts aligned with FastAPI schemas
- `shared/ui/` — reusable primitives (Button, Badge, Modal, Sidebar)

Vite proxies `/api/*` to `http://127.0.0.1:8000` during development. The frontend uses bearer-token auth (`VITE_API_TOKEN` env var) for protected endpoints. Dark/light theme persisted to `localStorage` under key `anomalyx-theme`.

## Key conventions

- Routing/auth: `/health` and `/metrics` are public; `/predict`, `/batch-score`, `/alerts`, and `/rules` require `Authorization: Bearer <AUTH_TOKEN>` via `api/dependencies/auth.py`.
- Error handling: `app/core/errors.py` and `app/main.py` normalize validation/domain errors into the uniform `{error:{code,message,details}}` envelope.
- Config: `core/config.py` builds cached `Settings` from env plus root `.env`; call `reset_settings_cache()` in tests after env changes. `AUTH_TOKEN` and `JWT_SECRET_KEY` are required. PostgreSQL creds are required only for `ALERT_REPOSITORY=postgres`; Supabase creds only for `ALERT_REPOSITORY=supabase`.
- Backend factories are env-switched and cached:
  - `repositories/factory.py`: `ALERT_REPOSITORY=in_memory|postgres|supabase`; PostgreSQL is primary persistence, Supabase is optional legacy.
  - `repositories/idempotency_factory.py`: `IDEMPOTENCY_STORE=in_memory|redis`.
  - `ml/factory.py`: `MOCK_ML_ENABLED` selects `MockPredictor` vs `XGBPredictor`. Factory uses `@lru_cache(maxsize=1)`; tests use a `reset_ml_cache` autouse fixture in `conftest.py` for predictor cache isolation.
- Rule DSL is sandboxed in `rules/engine.py` using AST validation. When adding rule inputs, update both `ALLOWED_CONTEXT_NAMES` and `features/service.py`.
- LLM guardrails: `llm/secure_data_wrapper.py` masks identifiers before prompting; `llm/explainer.py` rejects unsupported rule IDs/features or PII-looking output. Persisted `explanation_source` is `llm` or `template`.
- Metrics: `core/metrics.py` defines Prometheus metrics; `core/middleware.py` attaches request context and records request metrics.
- Cold-start features: `_compute_features` uses constant defaults for velocity/fan-out features. Do not remove these defaults without wiring Redis rolling aggregates first. `_PAYSIM_THRESHOLD` is in PaySim synthetic units, not VND — do not align to `CTR_THRESHOLD_VND` without retraining.

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
- stub OpenAI explainer calls,
- reset ML predictor cache (`reset_ml_cache`) for predictor isolation across tests.

Follow that pattern for API/service tests so default pytest never needs PostgreSQL, Redis, Supabase, or OpenAI.

Integration checks for external services belong in scripts or explicitly skipped tests; default `python -m pytest tests -q` should stay self-contained.

## Application Building Context

Read the following files in order before implementing or making any architectural decision:

1. `context/project-overview.md` — product definition, goals, features, and scope
2. `context/architecture.md` — system structure, boundaries, storage model, and invariants
3. `context/ui-context.md` — theme, colors, typography, and component conventions
4. `context/code-standards.md` — implementation rules and conventions
5. `context/ai-workflow-rules.md` — development workflow, scoping rules, and delivery approach
6. `context/progress-tracker.md` — current phase, completed work, open questions, and next steps

Update `context/progress-tracker.md` after each meaningful implementation change.

If implementation changes the architecture, scope, or standards documented in the context files, update the relevant file before continuing.
