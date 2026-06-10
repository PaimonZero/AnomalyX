# Hướng Dẫn Chạy Backend

## 1. Cài Dependencies

```powershell
python -m pip install -r backend/requirements.txt
```

Sau khi cài dependencies, vào thư mục backend:

```powershell
cd backend
```

## 2. Kiểm Tra Config

```powershell
python scripts/check_config.py
```

## 3. Kiểm Tra Supabase

Nếu chưa tạo bảng, chạy file `supabase/schema.sql` trong Supabase SQL Editor trước.

```powershell
python scripts/check_supabase.py
```

Kết quả mong muốn:

```text
REST root check: OK
alerts table check: OK
```

## 4. Kiểm Tra Redis

Hiện tại khi chạy local/dev, nên dùng in-memory idempotency để không cần Redis:

```env
IDEMPOTENCY_STORE=in_memory
```

Chỉ dùng Redis khi deploy, demo đầy đủ, hoặc đã có Redis server chạy sẵn:

```env
IDEMPOTENCY_STORE=redis
REDIS_URL=redis://localhost:6379/0
```

Khi bật Redis, kiểm tra bằng:

```powershell
python scripts/check_redis.py
```

Nếu lệnh trên báo `Connection refused`, nghĩa là Redis chưa chạy ở `localhost:6379`. Khi đó hoặc chạy Redis, hoặc đổi lại `IDEMPOTENCY_STORE=in_memory`.

## 5. Chạy Backend

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

## 6. Test Nhanh API

Health:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
```

Alerts:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/alerts
```

Metrics:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/metrics
```

## 7. Test Predict

```powershell
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
  -ContentType "application/json" `
  -Body $body
```

## 8. Chạy Unit Tests

```powershell
python -m pytest tests -q
```
