# AnomalyX

## Overview

AnomalyX is a backend-first AML transaction anomaly detection prototype for e-wallet transaction screening. It scores each transaction with a hybrid pipeline: deterministic YAML rules detect known AML typologies, a mockable ML predictor produces probabilistic risk, a decision engine reconciles both signals, and an asynchronous LLM explainer annotates flagged alerts with grounded, masked natural-language explanations. The prototype serves wallet backend services, compliance officers, and ML/risk engineers using synthetic or public data only.

## Goals

1. Provide real-time transaction risk scoring through `POST /api/v1/predict` with p95 latency ≤ 500 ms excluding external LLM calls.
2. Detect known AML patterns such as structuring, smurfing, rapid movement, layering, velocity anomaly, and threshold avoidance through configurable YAML rules.
3. Return explainable decisions containing `risk_score`, `risk_level`, `is_flagged`, `triggered_rules`, `top_features`, `model_version`, and optional alert metadata.
4. Create alerts for flagged transactions and let compliance reviewers escalate or dismiss alerts to create review labels.
5. Generate grounded LLM or template explanations without storing raw transaction payloads or raw PII.
6. Keep default tests self-contained with in-memory repositories and mock/stub external dependencies.

## Actors

- **Wallet Backend Service** — calls prediction APIs before confirming transactions and needs JSON responses plus idempotency for retries.
- **Compliance Officer** — reviews alert lists/details, reads explanations, and updates alert status to `ESCALATED` or `DISMISSED`.
- **ML/Risk Engineer** — monitors metrics, changes rule configuration, integrates real ML artifacts, and validates model quality.
- **LLM Provider** — external service used only for asynchronous explanation generation with masked, grounded context.

## Core User Flow

1. Wallet backend sends transaction payload to `POST /api/v1/predict` with bearer auth and optional `Idempotency-Key`.
2. API validates schema and claims idempotency key, defaulting to `transaction_id` when no header is supplied.
3. Feature service builds current feature context from transaction fields, optional geo/device evidence, and proxy rolling-aggregate features.
4. Rule engine evaluates active YAML rules over sandboxed DSL conditions.
5. ML predictor returns `risk_score`, `model_version`, and `top_features`; current working mode is deterministic mock ML.
6. Decision engine applies rule overrides and ML thresholds to produce `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.
7. Flagged `HIGH` or `CRITICAL` predictions create alerts; every prediction attempts a prediction audit log write.
8. API returns synchronous prediction response; LLM explanation runs later in a FastAPI background task for flagged alerts.
9. Compliance officer lists alerts, opens an alert, reads rule/feature evidence and explanation, then dismisses or escalates it.
10. Reviewer action updates alert status and writes a review label for future model retraining.

## Features

### Prediction Scoring

- `POST /api/v1/predict` for single real-time scoring.
- `POST /api/v1/batch-score` for multiple independent transaction scores in one request.
- Partial batch failure handling through per-item `results` and `errors`.
- Idempotency via in-memory or Redis-backed claim/store flow.

### Rule Engine

- YAML rules loaded from `configs/rules.yaml`.
- Sandboxed AST-based condition evaluator with whitelisted names and operators.
- Current rules cover threshold avoidance, structuring, smurfing, rapid movement, layering, velocity anomaly, optional geo/device anomaly, and large cash-out.
- Optional geo/device rule evidence is neutral without historical profile/Redis aggregate support; providing `device_id`, `location_country`, or `location_region` alone does not create risk.
- Hot reload via `POST /api/v1/rules/reload`; invalid configs must be rejected without replacing previous valid rules.
- Active rule inspection via `GET /api/v1/rules`.

### ML Prediction

- `ModelPredictor` interface supports mock and future real predictors.
- Current mock predictor is selected with `MOCK_ML_ENABLED=true`.
- Future `RealModelPredictor` must load serialized preprocessor/model artifacts and output same contract.

### Decision and Alerts

- `CRITICAL` rule severity overrides all ML scores and flags transaction as `CRITICAL`.
- `HIGH` rule severity overrides ML score and flags transaction as `HIGH`.
- ML score ≥ `RISK_THRESHOLD_FLAG` flags transaction as `HIGH` when no higher rule override exists; deprecated `RISK_THRESHOLD_HIGH` is only a fallback for unset `RISK_THRESHOLD_FLAG`.
- ML score ≥ `RISK_THRESHOLD_MEDIUM` produces `MEDIUM` log-only risk.
- Alerts store only derived risk evidence, status, explanations, and timestamps.

### LLM Explanation

- Explanation is asynchronous and never blocks prediction response.
- Prompt context is masked through secure data wrapper before calling external LLM.
- Unsupported or failed LLM outputs fall back to deterministic template text.
- Persisted `explanation_source` is `llm` or `template`.

### Observability and Operations

- Public health and metrics endpoints.
- JSON logging through backend logging setup.
- Prometheus metrics for request, prediction, and explanation behavior.
- Preflight scripts validate config, PostgreSQL, Redis, and optional Supabase connectivity.

## Scope

### In Scope

- Backend-only FastAPI AML prototype.
- Synthetic/public data workflow; no real e-wallet data.
- Rule + ML + decision + alert + explanation pipeline.
- PostgreSQL primary persistence with in-memory test/local mode and optional legacy Supabase adapter.
- Redis/in-memory idempotency store.
- OpenAPI-backed JSON API surface under `/api/v1`.
- Docker Compose infrastructure for PostgreSQL and Redis.
- Self-contained pytest suite for default development.

### Out of Scope

- Real transaction processing or funds movement.
- Regulatory STR/FIU/SBV submission; only simulated outputs.
- Production-scale streaming and deployment hardening.
- Real ML training/retraining and model artifact generation pipelines remain out of scope; runtime inference implementations such as `XGBPredictor` and pre-built inference artifacts may exist while the full `RealModelPredictor` training path remains pending.
- React frontend in current implementation; dashboard remains future work.
- Raw PII storage or raw transaction payload persistence.
- Redis rolling aggregate implementation; current feature service uses proxy values.
- Real drift detection and explanation cache; schema/design may exist, runtime wiring incomplete.

## Success Criteria

1. `python -m pytest tests -q` passes from `backend/` without PostgreSQL, Redis, Supabase, or OpenAI.
2. Quick local mode works with `ALERT_REPOSITORY=in_memory`, `IDEMPOTENCY_STORE=in_memory`, required secrets, and `MOCK_ML_ENABLED=true`.
3. `POST /api/v1/predict` returns a valid prediction contract and creates an alert only when `is_flagged=true`.
4. Repeated request with same idempotency key returns cached response and does not create duplicate alerts.
5. Flagged alert explanation path masks sensitive context and falls back to template on LLM failure.
6. PostgreSQL mode persists alerts, review labels, and prediction logs according to `backend/db/schema.sql`.
7. Protected business endpoints require `Authorization: Bearer <AUTH_TOKEN>`; `/health` and `/metrics` stay public.
8. No implementation stores raw transaction payloads or raw PII.
