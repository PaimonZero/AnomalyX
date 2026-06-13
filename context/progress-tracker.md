# Progress Tracker

Update this file after every meaningful implementation change.

## Current Phase

- Backend-first prototype implemented; context documentation initialized from `documents/` and current source code.

## Current Goal

- Keep six-file context accurate while finishing remaining prototype gaps: real ML integration, optional frontend/dashboard, Redis rolling aggregates, explanation cache, drift checks, and deployment packaging.

## Completed

- FastAPI backend skeleton under `backend/app/`.
- Versioned API router under `/api/v1`.
- Public health and metrics routes.
- Bearer-token protection for prediction, batch scoring, alerts, and rules routes.
- Runtime config loader from environment plus repo-root `.env`.
- Runtime secret validation for `AUTH_TOKEN` and `JWT_SECRET_KEY`.
- Uniform error envelope infrastructure.
- Prediction flow through idempotency, rule engine, mock ML predictor, decision engine, alert creation, audit log attempt, and async explanation.
- Single prediction endpoint: `POST /api/v1/predict`.
- Batch scoring endpoint: `POST /api/v1/batch-score` with partial failure reporting.
- YAML rule engine with sandboxed AST condition evaluator.
- Rule reload endpoint and active rules endpoint.
- Feature service with transaction features and proxy rolling-aggregate values.
- Decision engine with `CRITICAL`/`HIGH` rule override and configurable ML thresholds.
- Mock ML predictor and predictor factory.
- Alert service and repository abstractions.
- In-memory alert repository for tests/local mode.
- PostgreSQL alert repository and schema for alerts, review labels, prediction logs, feature snapshots, rule versions, and model registry.
- Optional legacy Supabase alert repository.
- In-memory and Redis idempotency repositories with claim-before-work behavior.
- OpenAI-based LLM explainer path with secure data wrapper and template fallback.
- JSON logging and Prometheus metrics infrastructure.
- Preflight scripts for config, PostgreSQL, Redis, and Supabase.
- Backend run guide in `documents/Backend_Run_Guide.md`.
- Remaining roadmap in `documents/Remaining_Project_Roadmap.md`.
- Six context files populated from templates on 2026-06-12.
- ML model integration (branch `model`, 2026-06-12):
  - `ml/` folder added: training notebooks (01–05), trained artifacts (`xgb_aml_v1.json` AUC-ROC=0.9999, `lgb_aml_v1.txt`, `rf_baseline.pkl` via Git LFS), `model_config.json`, `aml_rules.yaml`, `Makefile` with `make pipeline`.
  - `XGBPredictor` implemented in `backend/app/ml/xgb_predictor.py`; maps `TransactionRequest` to 26 PaySim features, runs XGBoost inference, returns SHAP top-5.
  - `backend/app/ml/factory.py` updated: `@lru_cache(maxsize=1)` + lazy `XGBPredictor` load when `MOCK_ML_ENABLED=false`.
  - `backend/app/core/config.py`: `model_path`/`model_config_path` settings with `PROJECT_ROOT`-based defaults; fail-fast validation checks artifact files exist at startup when `MOCK_ML_ENABLED=false`.
  - `backend/Dockerfile` added: non-root `appuser`, production-ready uvicorn CMD.
  - `docker-compose.yml` updated: `api` service added; full stack starts with a single `docker compose up`.
  - `backend/requirements.txt` updated: `xgboost>=2.1`, `shap>=0.45`, `numpy>=1.26`.
  - `.gitattributes` added: Git LFS tracking for `*.pkl`, `*.parquet`, `*.csv`.
  - `.env.example` updated with `MODEL_PATH`, `MODEL_CONFIG_PATH`, `MOCK_ML_ENABLED` guidance.
  - `backend/tests/conftest.py`: `reset_ml_cache` autouse fixture added for predictor cache isolation.
  - `/health` endpoint now reports real `model_version` from predictor instead of static `"external"`.
- Configuration docs now mark `RISK_THRESHOLD_HIGH` as deprecated fallback for `RISK_THRESHOLD_FLAG`.
- Background alert explanation failures are logged with alert/transaction context and emit bounded failure/latency metrics.
- Supabase schema now documents service-role RLS bypass, adds `alerts.is_flagged`, and includes schema-ready `feature_snapshots`, `rule_versions`, and `model_registry` tables.
- Roadmap/run-guide docs now match bearer-token auth and avoid fixed pytest pass counts.
- Project overview now separates ML training/artifact generation scope from existing runtime inference artifacts.
- README/CLAUDE examples now use placeholder secrets, README targets Python 3.11+, and PostgreSQL docs prefer `POSTGRES_*` over duplicated `DATABASE_URL` examples.
- Config loading now preserves intentionally empty environment variables over `.env`, builds `DATABASE_URL` from `POSTGRES_*` by default, and requires transaction currency in request payloads.
- JSON log timestamps now use `LogRecord.created` rather than formatter execution time.
- Auth token validation now uses constant-time comparison; alert service calls typed prediction-log repository methods directly; health/idempotency/model diagnostics now log clearer failure details.
- Idempotency corrupt-cache reclaim now uses atomic repository compare-and-replace; ML requirements are exact-pinned; scripts share URL masking; Docker Compose uses env-sourced PostgreSQL secrets with production secrets guidance; ML notebooks use timezone-aware timestamps and stripped feature-engineering outputs.
- `ml/rules/aml_rules.yaml` now uses backend rule-engine schema and whitelisted feature names only.
- README, CLAUDE guidance, backend run guide, env examples, and ML rule notebook notes now align with current ML/artifact state, `POSTGRES_*` config, placeholders, and bearer-token auth.

## In Progress

- Training data (`ml/data/raw/*.csv`, `ml/data/processed/*.parquet`) not committed; must run `make pipeline` inside `ml/` to regenerate artifacts locally. Raw PaySim CSV is excluded from version control because of its 493 MB size.

## Next Up

1. **W4 — Redis rolling aggregates**: wire real `tx_count_sender`, `fan_out_orig`, etc. from Redis into `_compute_features`; cold-start defaults currently bias scores toward false negatives on high-velocity patterns.
2. **W5 — Unit tests for `XGBPredictor`**: add pytest tests covering feature mapping, prediction contract, SHAP fallback, and cold-start path.
3. **Frontend dashboard scaffold**: React + Vite + Tailwind + shadcn/ui per `ui-context.md` spec.
4. **Explanation cache**: wire schema-ready `feature_snapshots`/explanation store.
5. **Drift metric implementation**: wire real drift detection from `model_registry` and metrics.
6. Update `.env.example` or docs if runtime configuration changes.
7. Keep context files synchronized as implementation evolves.

## Open Questions

- Cold-start historical features (`tx_count_sender`, `fan_out_orig`, etc.) use constant defaults — when will Redis rolling aggregates be implemented? Until then fraud scores for high-velocity patterns are suppressed.
- `_PAYSIM_THRESHOLD = 200_000` is in PaySim synthetic units; if model is retrained on VND data this constant and related flag features must be recalibrated against `CTR_THRESHOLD_VND`.
- `balance_diff_dest` is always 0 when `new_bal_dest` is computed from the same request; this feature only has variance in the raw PaySim CSV due to reporting inconsistencies. Consider removing it from the live feature vector or sourcing real account state.
- Should Supabase remain as legacy optional adapter or be removed from product docs and dependency expectations?
- Should auth stay service-token only for the prototype, or should frontend work introduce user/session-based auth?
- Should batch scoring stay request-body based, or should it support stored time-window queries after prediction logs mature?
- Should explanation language remain `vi,en`, Vietnamese-only, or user-selectable per request?

## Architecture Decisions

- Backend-first modular monolith: simpler prototype deployment and testability.
- Rule engine and ML predictor remain separate; decision engine owns final risk reconciliation.
- `CRITICAL` and `HIGH` rule severities override ML score; ML threshold can independently flag high-risk transactions.
- Idempotency key defaults to `transaction_id`, with optional `Idempotency-Key` header override.
- Idempotency claim happens before rule/ML/alert side effects to avoid duplicate alerts under concurrent retries.
- LLM explanations run asynchronously after the synchronous prediction response.
- PostgreSQL is primary persistence target; in-memory mode supports tests and quick local runs; Supabase is optional legacy.
- Redis is optional for idempotency runtime; default tests use in-memory store.
- Raw transaction payloads and raw PII are excluded from persistence and LLM prompt context.
- Context files are required working specs and must be updated when behavior, architecture, scope, or standards change.

## Session Notes

- Context files were templates before this update and now contain project-specific content based on PRD/TDD, roadmap, run guide, and inspected backend source.
- Current implementation differs from early TDD in some areas:
  - backend exists, frontend does not;
  - real `XGBPredictor` now available; mock ML (`MOCK_ML_ENABLED=true`) remains default for tests and local quick mode;
  - Redis rolling aggregates are not wired, `_compute_features` uses cold-start constant defaults;
  - PostgreSQL is primary persistence, Supabase optional legacy;
  - explanation cache and real drift detection remain gaps.
- Use `CLAUDE.md` command guidance: backend commands run from `backend/` unless noted.
- Quick local `.env` mode should use in-memory alert/idempotency stores and `MOCK_ML_ENABLED=true`.
- Full Docker stack (PostgreSQL + Redis + API): `docker compose up` from repo root.
- To use real ML: run `make pipeline` inside `ml/`, then set `MOCK_ML_ENABLED=false` with `MODEL_PATH` pointing to `ml/models/artifacts/xgb_aml_v1.json`.
