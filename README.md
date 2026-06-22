# AnomalyX - AML Transaction Anomaly Detector Backend

AnomalyX is a backend-only FastAPI prototype for Anti-Money Laundering (AML) transaction scoring. It validates transactions, computes serving-time features, runs YAML rules and mock ML inference, reconciles risk with a decision engine, persists audit/alert records, and asynchronously generates grounded alert explanations.

This repository currently does **not** include a React frontend or production ML training/retraining pipeline. Runtime inference implementations and pre-built model artifacts may exist; mock ML remains the default unless `MOCK_ML_ENABLED=false`.

## Current capabilities

- Real-time scoring: `POST /api/v1/predict`
- Batch scoring over supplied transactions: `POST /api/v1/batch-score`
- Alert listing/detail/status update
- Rule hot reload from `configs/rules.yaml`
- Prometheus metrics and health/readiness endpoint
- Bearer service-token auth for protected endpoints
- PostgreSQL primary alert/audit storage (`ALERT_REPOSITORY=postgres`)
- Optional in-memory alert/audit storage for tests and quick local runs
- Optional legacy Supabase REST alert/audit adapter
- In-memory or Redis-backed idempotency store
- OpenAI-based LLM explainer with deterministic template fallback
- Mock ML predictor fallback (`mock-ml-v1`) by default; optional `XGBPredictor` runtime inference when `MOCK_ML_ENABLED=false` and artifacts are present.

## Repository layout

```text
backend/
  app/
    api/                 FastAPI routers and auth dependency
    core/                config, logging, middleware, metrics, errors
    features/            shared serving-time feature computation
    llm/                 SecureDataWrapper + explainer/fallback guardrails
    ml/                  predictor interface + deterministic mock predictor
    repositories/        in-memory, PostgreSQL, Supabase, Redis-backed adapters
    rules/               YAML safe-DSL rule engine and hot-reload manager
    schemas/             Pydantic API models
    services/            prediction, alert, idempotency orchestration
  db/schema.sql          PostgreSQL schema
  scripts/               config/PostgreSQL/Supabase/Redis preflight checks
  tests/                 pytest suite
configs/rules.yaml       Active AML rule configuration
supabase/schema.sql      Optional legacy Supabase schema
docker-compose.yml       PostgreSQL + Redis for local infrastructure
.env.example             Root-level environment template
```

## Setup

Use Python 3.11+.

```bash
python -m pip install -r backend/requirements.txt
cp .env.example .env
```

`.env` lives at the repository root, not inside `backend/`.

For quick local development without external services, use:

```env
ALERT_REPOSITORY=in_memory
IDEMPOTENCY_STORE=in_memory
AUTH_TOKEN=<AUTH_TOKEN>
JWT_SECRET_KEY=<JWT_SECRET_KEY>
MOCK_ML_ENABLED=true
```

`OPENAI_API_KEY` is optional. If missing, the explainer uses deterministic template output.

## Local PostgreSQL + Redis

Start local infrastructure:

```bash
docker compose up -d postgres redis
```

Docker Compose reads PostgreSQL credentials from your shell or root `.env`; set `POSTGRES_PASSWORD` before starting the stack. Local Compose is for development only. Production deployments must use a secrets manager, Vault, Docker secrets, or equivalent platform secret store instead of committed literal credentials.

Use PostgreSQL persistence:

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
```

`backend/db/schema.sql` is mounted into the Postgres container as an init script. For an existing database, apply that schema manually.

## Run backend

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger UI: <http://localhost:8000/docs>

## Test and preflight

No linter/formatter is configured. Use pytest and the preflight scripts as quality gates.

```bash
cd backend
python -m pytest tests -q
python -m pytest tests/test_prediction_api.py -q
python -m pytest tests/test_prediction_api.py::test_predict_rejects_invalid_payload -q

python scripts/check_config.py
python scripts/check_postgres.py  # active only when ALERT_REPOSITORY=postgres
python scripts/check_supabase.py  # active only when ALERT_REPOSITORY=supabase
python scripts/check_redis.py     # active only when IDEMPOTENCY_STORE=redis
```

## Authentication

Protected endpoints require:

```http
Authorization: Bearer <AUTH_TOKEN>
```

Public endpoints:

- `GET /api/v1/health`
- `GET /api/v1/metrics`

Protected endpoints:

- `POST /api/v1/predict`
- `POST /api/v1/batch-score`
- `GET /api/v1/alerts`
- `GET /api/v1/alerts/{alert_id}`
- `PATCH /api/v1/alerts/{alert_id}/status`
- `GET /api/v1/rules`
- `POST /api/v1/rules/reload`

## API examples

### Predict

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Authorization: Bearer <AUTH_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx_demo_001",
    "sender_id": "h:sender001",
    "receiver_id": "h:receiver001",
    "sender_balance": 500000000,
    "receiver_balance": 200000,
    "amount": 380000000,
    "currency": "VND",
    "timestamp": "2026-05-30T09:14:03+07:00",
    "channel": "TRANSFER"
  }'
```

Response includes:

- `transaction_id`
- `risk_score`
- `risk_level`
- `is_flagged`
- `model_version`
- `triggered_rules`
- `top_features`
- `explanation_source`
- `alert_id`

Malformed payloads return HTTP 400 with:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "details": {}
  }
}
```

Repeated `transaction_id` or `Idempotency-Key` returns the original prediction without rerunning scoring.

### Batch score

```bash
curl -X POST http://localhost:8000/api/v1/batch-score \
  -H "Authorization: Bearer <AUTH_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_id": "batch_demo_001",
    "transactions": [
      {
        "transaction_id": "tx_batch_001",
        "sender_id": "h:sender001",
        "receiver_id": "h:receiver001",
        "sender_balance": 500000000,
        "receiver_balance": 200000,
        "amount": 380000000,
        "currency": "VND",
        "timestamp": "2026-05-30T09:14:03+07:00",
        "channel": "TRANSFER"
      }
    ]
  }'
```

Batch scoring currently scores transactions supplied in the request. It does not yet query historical time windows from PostgreSQL.

### Alert review

```bash
curl -X PATCH http://localhost:8000/api/v1/alerts/al_example/status \
  -H "Authorization: Bearer <AUTH_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"status":"ESCALATED","reviewer_id":"reviewer_001"}'
```

Allowed statuses:

- `NEW`
- `ESCALATED`
- `DISMISSED`

Escalated/dismissed reviews create review-label records for future retraining.

### Rules

```bash
curl -H "Authorization: Bearer <AUTH_TOKEN>" http://localhost:8000/api/v1/rules

curl -X POST \
  -H "Authorization: Bearer <AUTH_TOKEN>" \
  http://localhost:8000/api/v1/rules/reload
```

Rules live in `configs/rules.yaml`. The rule engine uses a safe AST-based DSL. If reload fails, the previous valid rule set remains active.

Initial rules cover threshold avoidance, structuring, smurfing, rapid movement, layering, velocity anomaly, and large cash-out patterns using available request-derived features.

## Persistence

### In-memory mode

Use this for tests and quick local development:

```env
ALERT_REPOSITORY=in_memory
IDEMPOTENCY_STORE=in_memory
```

### PostgreSQL mode

PostgreSQL is the primary persistent alert/audit backend:

```env
ALERT_REPOSITORY=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=anomalyx
POSTGRES_USER=anomalyx_user
POSTGRES_PASSWORD=<POSTGRES_PASSWORD>
POSTGRES_SSLMODE=disable
```

Stored data is limited to transaction IDs, prediction outputs, derived feature/rule evidence, alert review metadata, explanations, and timestamps. Raw transaction payloads and raw PII are not stored.

PostgreSQL schema includes:

- `alerts`
- `review_labels`
- `prediction_logs`
- `feature_snapshots` (schema-ready, not wired into scoring flow yet)
- `rule_versions` (schema-ready, not wired into rule reload yet)
- `model_registry` (schema-ready, no real model artifact yet)

### Optional legacy Supabase adapter

Supabase REST remains available as a legacy adapter:

```env
ALERT_REPOSITORY=supabase
SUPABASE_URL=https://...
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_SCHEMA=public
```

Run `supabase/schema.sql` in Supabase SQL Editor before use.

### Redis

Redis can store idempotency keys:

```env
IDEMPOTENCY_STORE=redis
REDIS_URL=redis://localhost:6379/0
```

Redis rolling aggregate features and explanation cache are planned but not fully implemented yet.

## LLM explanation behavior

Flagged alerts trigger a FastAPI background task. Before calling the LLM, `SecureDataWrapper` masks identifiers and sends only grounded context:

- triggered rule IDs/severity/typology
- risk score and risk level
- top features
- masked non-PII transaction metadata

If the provider fails or produces unsupported claims, the system stores a deterministic template explanation with `explanation_source = "template"`. Successful provider output is stored as `explanation_source = "llm"`.

## Remaining gaps vs PRD/TDD

- No React/Vite compliance dashboard is included.
- Production ML training/retraining and artifact generation remain out of scope; `MOCK_ML_ENABLED=true` is the default working mode.
- Runtime `XGBPredictor` inference and pre-built artifacts may exist for optional real-model mode when `MOCK_ML_ENABLED=false`.
- Redis rolling aggregate features and explanation cache are placeholders/TODOs.
- Real drift detection is a Prometheus placeholder metric, not a PSI/KS implementation.
- PostgreSQL `feature_snapshots`, `rule_versions`, and `model_registry` tables are schema-ready but not fully wired into application workflows yet.
