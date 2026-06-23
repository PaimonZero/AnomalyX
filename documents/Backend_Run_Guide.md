# Hướng Dẫn Chạy Backend

Backend được phát triển bằng FastAPI. Chạy lệnh từ repo root hoặc thư mục `backend/` theo hướng dẫn cụ thể dưới đây.

---

## 1. Hướng Dẫn Chạy Bằng Docker Compose (Khuyên Dùng)

Đây là cách nhanh nhất và chuẩn nhất để chạy toàn bộ hệ thống backend (bao gồm API Service, PostgreSQL database và Redis cache).

### Bước 1: Tạo file `.env`
Sao chép `.env.example` ở repo root thành `.env`:
```powershell
cp .env.example .env
```
Mở file `.env` và thiết lập các giá trị bảo mật bắt buộc:
* `AUTH_TOKEN` và `JWT_SECRET_KEY` phải dài ít nhất 32 ký tự.
* Cập nhật `POSTGRES_PASSWORD` thành mật khẩu tùy chọn của bạn (ví dụ: `anomalyx_password`).

### Bước 2: Khởi động Docker Compose
Từ thư mục root của dự án, chạy lệnh:
```powershell
docker compose up --build -d
```
Lệnh này sẽ xây dựng container cho FastAPI API, khởi chạy PostgreSQL (cổng host `5435`, cổng container `5432`) và khởi chạy Redis (cổng `6379`).

### Bước 3: Kiểm tra Logs và Trạng thái
Để kiểm tra logs của FastAPI API:
```powershell
docker compose logs -f api
```

### Bước 4: Chạy Preflight Checks inside Docker
Để đảm bảo kết nối DB và Redis trong container đã hoàn toàn sẵn sàng, chạy các lệnh:
```powershell
docker compose exec api python scripts/check_config.py
docker compose exec api python scripts/check_postgres.py
docker compose exec api python scripts/check_redis.py
```

---

## 2. Hướng Dẫn Chạy Trực Tiếp (Không Dùng Docker cho API)

Nếu muốn chạy trực tiếp file Python trên máy host (để phát triển hoặc debug cục bộ), hãy làm theo các bước dưới đây.

### Bước 1: Khởi động PostgreSQL và Redis
Vẫn sử dụng Docker để khởi chạy cơ sở hạ tầng nền tảng:
```powershell
docker compose up -d postgres redis
```
*Lưu ý: PostgreSQL sẽ chạy trên cổng `5435` ở máy host.*

### Bước 2: Cài đặt Python Dependencies
Khuyên dùng Python 3.11+. Từ repo root, chạy lệnh:
```powershell
python -m pip install -r backend/requirements.txt
```

### Bước 3: Cấu hình cổng PostgreSQL trong `.env`
Khi chạy API trực tiếp trên máy host, bạn cần cấu hình cổng PostgreSQL kết nối là `5435`:
```env
ALERT_REPOSITORY=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5435
POSTGRES_DB=anomalyx
POSTGRES_USER=anomalyx_user
POSTGRES_PASSWORD=<MẬT_KHẨU_ĐÃ_ĐẶT_Ở_BƯỚC_1>
IDEMPOTENCY_STORE=redis
REDIS_URL=redis://localhost:6379/0
```

### Bước 4: Chạy Preflight Checks cục bộ
Di chuyển vào thư mục `backend/` và chạy các kịch bản kiểm tra:
```powershell
cd backend
python scripts/check_config.py
python scripts/check_postgres.py
python scripts/check_redis.py
```

### Bước 5: Khởi động API
```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger UI sẽ có sẵn tại: <http://localhost:8000/docs>

---

## 3. Chạy Unit Tests & Đo Code Coverage

Các bộ kiểm thử tự động sử dụng kho dữ liệu In-Memory để không cần kết nối thật đến PostgreSQL hay Redis khi chạy mặc định.

Từ thư mục `backend/`, chạy lệnh kiểm thử:
```powershell
cd backend
python -m pytest tests -v
```

Để đo lường độ bao phủ mã nguồn (Code Coverage):
```powershell
python -m pytest --cov=app tests
```
Mục tiêu độ bao phủ yêu cầu là `>= 70%` (hiện tại đạt **78%**).

---

## 4. Các Endpoint API Chính

Tất cả các endpoint nghiệp vụ đều yêu cầu truyền Bearer token trong Header:
```http
Authorization: Bearer <AUTH_TOKEN>
```

### 4.1. Dự đoán giao dịch đơn lẻ (`POST /api/v1/predict`)

> [!NOTE]
> Các trường `device_id`, `location_country`, và `location_region` là hoàn toàn **không bắt buộc (optional)**. Bạn có thể bỏ qua chúng trong payload nếu không có dữ liệu; hệ thống sẽ tự động gán giá trị mặc định là `None`, và bỏ qua các quy tắc kiểm tra Geo/Device anomaly mà không gây lỗi logic hay kích hoạt cảnh báo giả.

```powershell
$headers = @{ Authorization = "Bearer test-service-token-strong-000000000000" }

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
  device_id = "device-demo-001"
  location_country = "VN"
  location_region = "HN"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://localhost:8000/api/v1/predict `
  -Method POST `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

### 4.2. Dự đoán giao dịch theo lô (`POST /api/v1/batch-score`)
```powershell
$headers = @{ Authorization = "Bearer test-service-token-strong-000000000000" }

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

### 4.3. Theo dõi Drift Giao Dịch
* **Xem trạng thái Drift hiện tại (PSI):**
  ```powershell
  Invoke-RestMethod -Uri http://localhost:8000/api/v1/drift/status -Headers $headers
  ```
* **Cập nhật phân phối Baseline:**
  ```powershell
  $body = @{ scores = @(0.05, 0.05, 0.1, 0.2, 0.05) } | ConvertTo-Json
  Invoke-RestMethod -Uri http://localhost:8000/api/v1/drift/baseline -Method POST -Headers $headers -ContentType "application/json" -Body $body
  ```
