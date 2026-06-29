# AnomalyX - AML Transaction Anomaly Detector

AnomalyX is a prototype Anti-Money Laundering (AML) system for scoring suspicious transactions. The system combines:

- FastAPI backend
- React/Vite frontend
- YAML rule engine
- Mock or real ML predictor
- PostgreSQL alert/audit storage
- Redis idempotency store
- Optional LLM explanation fallback

## Main features

- Single transaction scoring: `POST /api/v1/predict`
- Batch scoring: `POST /api/v1/batch-score`
- Alert list/detail/status update
- Active AML rules from `configs/rules.yaml`
- Apply updated rules to backend: `POST /api/v1/rules/reload`
- Health and Prometheus metrics
- Bearer token protection for protected APIs
- Frontend pages:
  - Alerts
  - Single Prediction
  - Batch Scoring
  - Monitoring

## Repository layout

```text
backend/                 FastAPI backend
frontend/                React/Vite frontend
configs/rules.yaml       Active AML rule configuration
ml/models/artifacts/     Optional real ML model artifacts
docker-compose.yml       Docker stack: api + postgres + redis
.env.example             Environment template
documents/               Project documents and run guides
```

## Docker services

`docker-compose.yml` starts 3 services:

| Service | Image/build | Port | Purpose |
|---|---|---:|---|
| `api` | built from `backend/Dockerfile` | `8000` | AnomalyX backend |
| `postgres` | `postgres:16` | `5432` | Alert/audit database |
| `redis` | `redis:7` | `6379` | Idempotency store |

The backend container mounts:

```yaml
./configs:/configs:ro
./ml/models/artifacts:/app/ml/models/artifacts:ro
```

So the backend can read:

```text
/configs/rules.yaml
/app/ml/models/artifacts/xgb_aml_v1.json
```

## 1. Create `.env`

From repo root:

```powershell
Copy-Item .env.example .env
```

Update these required values in `.env`:

```env
AUTH_TOKEN=local-service-token-change-me-000000
JWT_SECRET_KEY=local-jwt-secret-change-me-000000

ALERT_REPOSITORY=postgres
IDEMPOTENCY_STORE=redis

POSTGRES_DB=anomalyx
POSTGRES_USER=anomalyx_user
POSTGRES_PASSWORD=local-postgres-password-change-me
POSTGRES_SSLMODE=disable

MOCK_ML_ENABLED=true

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174
```

Do not commit `.env`.

## 2. Start backend stack with Docker

Build and start:

```powershell
docker compose up --build -d
```

Check containers:

```powershell
docker compose ps
```

Expected services:

```text
api
postgres
redis
```

View backend logs:

```powershell
docker compose logs -f api
```

Stop all services:

```powershell
docker compose down
```

Reset local database volume:

```powershell
docker compose down -v
```

Use `down -v` only when you intentionally want to delete local PostgreSQL data.

## 3. Check backend

Swagger UI:

```text
http://localhost:8000/docs
```

Health:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
```

Metrics:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/metrics
```

## 4. Run frontend

Frontend is not inside Docker Compose yet. Run it separately:

```powershell
cd frontend
npm install
npm run dev
```

Frontend environment should point to Docker backend:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

In the frontend sidebar, enter the same bearer token from `.env`:

```text
local-service-token-change-me-000000
```

If Vite runs on `http://localhost:5174`, make sure `.env` backend has:

```env
CORS_ORIGINS=http://localhost:5174,http://127.0.0.1:5174
```

## 5. Test protected API

Protected endpoints require:

```http
Authorization: Bearer <AUTH_TOKEN>
```

Example predict request:

```powershell
$headers = @{ Authorization = "Bearer local-service-token-change-me-000000" }

$body = @{
  transaction_id = "tx_demo_001"
  sender_id = "h:sender001"
  receiver_id = "h:receiver001"
  sender_balance = 500000000
  receiver_balance = 200000
  amount = 380000000
  currency = "VND"
  timestamp = "2026-05-30T09:14:03+07:00"
  channel = "TRANSFER"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://localhost:8000/api/v1/predict `
  -Method POST `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

## 6. Mock ML vs real ML

Default demo mode:

```env
MOCK_ML_ENABLED=true
```

This uses:

```text
backend/app/ml/mock_predictor.py
```

To use the real XGBoost model artifacts:

```env
MOCK_ML_ENABLED=false
```

Docker Compose already mounts:

```text
ml/models/artifacts/xgb_aml_v1.json
ml/models/artifacts/model_config.json
```

Restart after changing `.env`:

```powershell
docker compose down
docker compose up --build -d
```

Check `/health`. Real ML should show:

```json
{
  "model": {
    "mock_enabled": false,
    "version": "xgb_aml_v1"
  }
}
```

## 7. Rules reload

Rules live in:

```text
configs/rules.yaml
```

Because Docker mounts `./configs` into the API container, editing `configs/rules.yaml` on the host changes the file seen by the container.

After editing rules, call:

```powershell
$headers = @{ Authorization = "Bearer local-service-token-change-me-000000" }

Invoke-RestMethod `
  -Uri http://localhost:8000/api/v1/rules/reload `
  -Method POST `
  -Headers $headers
```

The backend reads the updated file and replaces the in-memory rule engine. If reload fails, the previous valid rules remain active.

## 8. Common issues

### `POSTGRES_PASSWORD is required`

Set this in `.env`:

```env
POSTGRES_PASSWORD=local-postgres-password-change-me
```

Then restart:

```powershell
docker compose up --build -d
```

### Backend exits because of insecure token

`AUTH_TOKEN` and `JWT_SECRET_KEY` must be non-default and at least 32 characters.

### Frontend CORS error

Add the frontend origin to backend `.env`:

```env
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174
```

Then rebuild/restart API:

```powershell
docker compose up --build -d api
```

### Backend cannot find `rules.yaml`

Make sure `docker-compose.yml` has:

```yaml
volumes:
  - ./configs:/configs:ro
```

## More documentation

- [Backend run guide](documents/Backend_Run_Guide.md)
- [Remaining project roadmap](documents/Remaining_Project_Roadmap.md)
