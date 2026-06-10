# Hướng Dẫn Chạy Backend

Backend chạy bằng FastAPI. Chạy lệnh từ repo root trừ khi có ghi chú `cd backend`.

## 1. Cài Dependencies

```powershell
python -m pip install -r backend/requirements.txt
```

## 2. Tạo `.env`

File `.env` nằm ở repo root, không nằm trong `backend/`.

Quick local mode, không cần PostgreSQL/Redis/Supabase:

```env
ALERT_REPOSITORY=in_memory
IDEMPOTENCY_STORE=in_memory
AUTH_TOKEN=local-service-token-change-me-000000
JWT_SECRET_KEY=local-jwt-secret-change-me-0000000
MOCK_ML_ENABLED=true
```

> `AUTH_TOKEN` và `JWT_SECRET_KEY` phải đủ dài, không dùng giá trị dev mặc định như `dev-service-token` hoặc `dev-jwt-secret`.

PostgreSQL + Redis mode:

```env
ALERT_REPOSITORY=postgres
DATABASE_URL=postgresql+psycopg://anomalyx_user:anomalyx_password@localhost:5432/anomalyx
IDEMPOTENCY_STORE=redis
REDIS_URL=redis://localhost:6379/0
AUTH_TOKEN=local-service-token-change-me-000000
JWT_SECRET_KEY=local-jwt-secret-change-me-0000000
MOCK_ML_ENABLED=true
```

## 3. Start Local Infrastructure

Chỉ cần nếu dùng PostgreSQL/Redis mode:

```powershell
docker compose up -d postgres redis
```

## 4. Vào Thư Mục Backend

```powershell
cd backend
```

## 5. Kiểm Tra Config

```powershell
python scripts/check_config.py
```

Nếu dùng PostgreSQL:

```powershell
python scripts/check_postgres.py
```

Nếu dùng Redis:

```powershell
python scripts/check_redis.py
```

Nếu vẫn dùng Supabase legacy:

```powershell
python scripts/check_supabase.py
```

## 6. Chạy Backend

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

## 7. Test Nhanh API

Health và metrics public:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
Invoke-RestMethod http://localhost:8000/api/v1/metrics
```

Các endpoint như `/predict`, `/batch-score`, `/alerts`, `/rules` cần bearer token:

```powershell
$headers = @{ Authorization = "Bearer local-service-token-change-me-000000" }
```

Alerts:

```powershell
Invoke-RestMethod `
  -Uri http://localhost:8000/api/v1/alerts `
  -Headers $headers
```

## 8. Test Predict

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

## 9. Test Batch Score

```powershell
$headers = @{ Authorization = "Bearer local-service-token-change-me-000000" }

$body = @{
  batch_id = "batch_demo_001"
  transactions = @(
    @{
      transaction_id = "tx_batch_001"
      sender_id = "h:sender001"
      receiver_id = "h:receiver001"
      sender_balance = 500000000
      receiver_balance = 200000
      amount = 380000000
      currency = "VND"
      timestamp = "2026-05-30T09:14:03+07:00"
      channel = "TRANSFER"
    },
    @{
      transaction_id = "tx_batch_002"
      sender_id = "h:sender002"
      receiver_id = "h:receiver002"
      sender_balance = 15000000
      receiver_balance = 200000
      amount = 9500000
      currency = "VND"
      timestamp = "2026-05-30T09:20:03+07:00"
      channel = "PAYMENT"
    }
  )
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Uri http://localhost:8000/api/v1/batch-score `
  -Method POST `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

Batch response có `predictions`, `flagged_predictions`, `errors`, và `results`. Nếu một transaction lỗi, các transaction còn lại vẫn có kết quả.

## 10. Chạy Unit Tests

Từ thư mục `backend/`:

```powershell
python -m pytest tests -q
```

Kết quả hiện tại mong muốn:

```text
59 passed
```
