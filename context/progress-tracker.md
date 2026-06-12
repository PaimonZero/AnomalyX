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
- Six context files populated from templates on 2026-06-12:
  - `context/project-overview.md`
  - `context/architecture.md`
  - `context/ui-context.md`
  - `context/code-standards.md`
  - `context/ai-workflow-rules.md`
  - `context/progress-tracker.md`

## In Progress

- Context docs now reflect backend-only current state and intended future scope.
- Optional geo/device transaction fields and neutral geo/device rule evidence were added to align with PRD/TDD geo/device anomaly scope without breaking existing payloads.
- If you need to track local changes or temporary state, save them in PR notes or session notes rather than in this tracker.

## Next Up

1. Run backend tests from `backend/` after context-doc update if validation is required:
   `python -m pytest tests -q`
2. Decide next implementation unit:
   - real ML predictor adapter and artifact contract,
   - Redis-backed rolling aggregate feature service,
   - frontend dashboard scaffold,
   - explanation cache,
   - drift metric implementation,
   - Docker backend service packaging.
3. Update `.env.example` or docs if runtime configuration changes.
4. Keep context files synchronized as implementation evolves.

## Open Questions

- Should next milestone prioritize real ML model integration or frontend dashboard for demo value?
- Should Supabase remain as legacy optional adapter or be removed from product docs and dependency expectations?
- Should auth stay service-token only for the prototype, or should frontend work introduce user/session-based auth?
- Should batch scoring stay request-body based, or should it support stored time-window queries after prediction logs mature?
- What exact artifact format should real ML use: pickle/joblib pipeline, ONNX, or separate preprocessor + model files?
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
  - mock ML is current working mode;
  - Redis rolling aggregates are not wired, feature service uses proxy values;
  - optional geo/device fields exist, but true geo/device anomaly detection still needs historical device/location profiles or Redis-backed aggregate history;
  - PostgreSQL is now primary persistence, Supabase optional legacy;
  - explanation cache and real drift detection remain gaps.
- Use `CLAUDE.md` command guidance: backend commands run from `backend/` unless noted.
- Quick local `.env` mode should use in-memory alert/idempotency stores and `MOCK_ML_ENABLED=true`.
