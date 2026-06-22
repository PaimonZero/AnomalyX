# Architecture Context

## Stack

| Layer | Technology | Role |
| --- | --- | --- |
| API framework | FastAPI + Uvicorn | Versioned JSON API, request validation, dependency injection, background tasks |
| Language/runtime | Python 3.11+ | Backend service, rule engine, feature service, ML adapter, repositories |
| Schemas | Pydantic | Request/response validation and OpenAPI schema generation |
| Rules | YAML + sandboxed AST DSL | Declarative AML typology detection over whitelisted feature context |
| ML | `ModelPredictor` interface + `XGBPredictor` (real XGB inference, optional when `MOCK_ML_ENABLED=false`) + `MockModelPredictor` (default when `MOCK_ML_ENABLED=true`) | Probabilistic `risk_score`, `model_version`, `top_features`; real XGBoost model trained on PaySim dataset (AUC-ROC≈0.9999) |
| Decision | Python service | Reconcile rule severity and ML thresholds into final risk level |
| Persistence | PostgreSQL + SQLAlchemy/psycopg | Alerts, review labels, prediction logs; schema-ready feature/model/rule tables |
| Local/test persistence | In-memory repositories | Self-contained tests and quick local mode |
| Legacy optional persistence | Supabase REST adapter | Optional legacy alert repository only |
| Idempotency | In-memory or Redis | Claim-before-work and response cache keyed by idempotency key |
| LLM | OpenAI explainer adapter + template fallback | Async alert explanations with masked context |
| Observability | JSON logging + Prometheus client | Request, prediction, explanation, and service metrics |
| Infrastructure | Docker Compose | PostgreSQL + Redis + FastAPI `api` service; single `docker compose up` starts full stack |
| Frontend | React + TypeScript + Vite + Tailwind CSS | Core AML demo shell, feature routes, typed API client, and theme system |
| Frontend state/routing | TanStack Query + React Router | Server-state lifecycle and feature-level navigation |

## System Boundaries

- `backend/app/api/` — FastAPI routers, route dependencies, versioned API composition.
- `backend/app/api/dependencies/auth.py` — bearer-token auth for protected business endpoints.
- `backend/app/schemas/` — Pydantic contracts for prediction, alerts, health, and error envelopes.
- `backend/app/services/` — application orchestration: prediction flow, alert workflow, idempotency behavior.
- `backend/app/core/` — settings, errors, decision logic, logging, metrics, middleware.
- `backend/app/features/` — feature computation shared by rules and future ML integration; current rolling values are proxy placeholders.
- `backend/app/rules/` — YAML rule loading, validation, safe condition evaluation, hot reload manager.
- `backend/app/ml/` — predictor protocol, mock predictor, predictor factory; real model adapter belongs here.
- `backend/app/llm/` — secure masking wrapper, prompt/explainer logic, LLM fallback behavior.
- `backend/app/repositories/` — alert and idempotency repository protocols plus in-memory/PostgreSQL/Supabase/Redis implementations.
- `backend/db/` — PostgreSQL schema and database migration baseline.
- `configs/` — repo-root runtime YAML rule configuration read by the service.
- `backend/scripts/` — operator preflight checks for config and external services.
- `backend/tests/` — self-contained unit/API tests with external services stubbed or forced in memory.
- `documents/` — PRD, TDD, roadmap, and run guide used as source requirements.
- `context/` — six-file implementation context that must stay synchronized with meaningful changes.
- `frontend/src/app/` — frontend bootstrap, providers, and route composition.
- `frontend/src/layouts/` — application-level layout shells.
- `frontend/src/features/` — business feature boundaries for Alerts, API Testing, Batch Scoring, and Monitoring.
- `frontend/src/shared/` — typed API infrastructure, contracts, configuration, and reusable UI.
- Frontend local development proxies `/api/*` through Vite to `http://127.0.0.1:8000`; Alerts, API Testing, Predict Batch, and Monitoring use real FastAPI endpoints. Protected workflows use `VITE_API_TOKEN` bearer auth; Monitoring reads public health and metrics endpoints.

## Runtime Request Flow

1. `POST /api/v1/predict` enters through `backend/app/api/v1/routes/prediction.py`.
2. `require_api_auth` checks `Authorization: Bearer <AUTH_TOKEN>` for protected routes.
3. `TransactionRequest` validates required transaction fields plus optional `device_id`, `location_country`, and `location_region` when provided.
4. `PredictionService.predict` claims idempotency key, defaulting to `transaction_id`.
5. Rule engine evaluates `configs/rules.yaml` over `FeatureService.compute(transaction).values`.
6. Predictor factory returns current predictor, normally `MockPredictor` when `MOCK_ML_ENABLED=true`.
7. Decision engine applies rule severity overrides and thresholds from settings.
8. Flagged predictions create alerts through `AlertService` and repository factory.
9. FastAPI background task runs `PredictionService.explain_alert` for flagged alerts.
10. Prediction audit log write is attempted after response construction; failures are logged without failing prediction.
11. Idempotency store saves successful response for future duplicate requests.

## Storage Model

- **PostgreSQL `alerts`**: flagged transaction records only: alert id, transaction id, risk score/level, rule evidence, feature evidence, explanation, status, reviewer, timestamps.
- **PostgreSQL `review_labels`**: compliance review labels derived from alert status changes.
- **PostgreSQL `prediction_logs`**: audit log for each prediction response: transaction id, risk output, model version, evidence, optional alert id.
- **PostgreSQL `feature_snapshots`**: schema-ready table for derived feature snapshots; not fully wired.
- **PostgreSQL `rule_versions`**: schema-ready table for rule config versions; not fully wired.
- **PostgreSQL `model_registry`**: schema-ready table for model artifact metadata; not fully wired.
- **Redis idempotency store**: atomic in-progress claim and serialized response cache with TTL.
- **In-memory repositories**: process-local alert/idempotency data for tests and quick local runs.
- **Supabase**: optional legacy alert repository; PostgreSQL is primary persistence target. The adapter uses a service-role key that bypasses RLS, and its alert/review column names follow the current REST adapter contract rather than being a full drop-in PostgreSQL schema mirror.
- **`.env` at repo root**: runtime configuration and secrets; never commit real secrets.

## Auth and Access Model

- `/api/v1/health` and `/api/v1/metrics` are public.
- `/api/v1/predict`, `/api/v1/batch-score`, `/api/v1/alerts`, and `/api/v1/rules` require `Authorization: Bearer <AUTH_TOKEN>`.
- `AUTH_TOKEN` and `JWT_SECRET_KEY` are required runtime secrets and must be at least 32 characters outside test overrides.
- Current auth model is service-token based, not per-user RBAC.
- `reviewer_id` is stored as provided by API payload; no user table/session model exists.
- Future frontend/user auth must not weaken existing service-token protection for backend integrations.

## Configuration Model

- `backend/app/core/config.py` loads env plus repo-root `.env`, preserving intentionally empty environment variables over `.env` values.
- `get_settings()` is cached; tests must call `reset_settings_cache()` after env changes.
- Repository selection:
  - `ALERT_REPOSITORY=in_memory|postgres|supabase`
  - `IDEMPOTENCY_STORE=in_memory|redis`
- ML selection:
  - `MOCK_ML_ENABLED=true` selects deterministic mock mode.
  - Real ML integration must keep `ModelPredictor` output contract.
- Risk thresholds:
  - `RISK_THRESHOLD_MEDIUM`, default `0.40`
  - `RISK_THRESHOLD_FLAG`, default `0.70`
  - `RISK_THRESHOLD_HIGH` is deprecated and used only as a fallback when `RISK_THRESHOLD_FLAG` is unset; use `RISK_THRESHOLD_FLAG` going forward.
- PostgreSQL is required only when `ALERT_REPOSITORY=postgres`; `DATABASE_URL` is built from `POSTGRES_*` by default and can be explicitly overridden when needed.
- Supabase credentials are required only when `ALERT_REPOSITORY=supabase`; the legacy adapter requires `SUPABASE_SERVICE_ROLE_KEY`, which bypasses Supabase RLS.
- Redis is required only when `IDEMPOTENCY_STORE=redis`.

## API Surface

- `GET /api/v1/health` — public liveness/config health.
- `GET /api/v1/metrics` — public Prometheus metrics.
- `POST /api/v1/predict` — protected single transaction scoring.
- `POST /api/v1/batch-score` — protected batch scoring with per-item results/errors.
- `GET /api/v1/alerts` — protected alert list.
- `GET /api/v1/alerts/{id}` — protected alert detail.
- `PATCH /api/v1/alerts/{id}/status` — protected alert review update.
- `GET /api/v1/rules` — protected active rule configuration.
- `POST /api/v1/rules/reload` — protected rule reload.

## Invariants

1. Raw transaction payloads must not be stored in PostgreSQL, logs, idempotency metadata beyond cached response, or LLM prompts.
2. Raw PII must not be accepted as a product assumption; identifiers are pseudonymous/hash-like and must be masked before LLM use.
3. Default `python -m pytest tests -q` from `backend/` must not require PostgreSQL, Redis, Supabase, OpenAI, or network access.
4. Business endpoints stay authenticated; only health and metrics remain public.
5. Prediction response shape must remain stable for wallet/frontend clients unless context docs and tests are updated first.
6. Idempotency claim must happen before rule/ML/alert side effects to avoid duplicate alerts under concurrent retries.
7. LLM explanation must run off the synchronous prediction path.
8. Rule DSL must stay sandboxed through AST validation; never use `eval` or arbitrary Python execution.
9. Adding rule input requires updating both `ALLOWED_CONTEXT_NAMES` and `FeatureService.compute`.
10. Optional geo/device inputs must remain backward-compatible; missing fields produce neutral feature values and must not trigger geo/device risk by themselves.
11. Invalid rule reload must not replace previous valid rule set.
12. Prediction audit write failure must be logged but must not fail successful prediction.
13. PostgreSQL schema must remain limited to transaction IDs, prediction outputs, derived feature/rule evidence, alert review metadata, explanations, and timestamps.
14. External service credentials must come from env only and must not be printed by scripts/logs.
15. If architecture, scope, or standards change, update relevant `context/*.md` before continuing implementation.
