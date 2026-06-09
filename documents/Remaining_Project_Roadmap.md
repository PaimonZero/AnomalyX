# Lộ Trình Các Phần Còn Lại Của AnomalyX

Tài liệu này tóm tắt những phần lớn còn lại của dự án sau khi đã triển khai backend-first prototype.

## 1. Trạng Thái Backend Hiện Tại

Đã làm:

- FastAPI backend skeleton.
- File `.env` và config loader.
- Mock ML adapter.
- Decision engine.
- YAML rule engine.
- API `POST /api/v1/predict`.
- Alert workflow.
- OpenAI LLM explanation với template fallback.
- Supabase persistence implementation.
- Redis/in-memory idempotency implementation với atomic claim-before-work để tránh tạo duplicate alert khi request trùng idempotency key chạy đồng thời.
- JSON logging và Prometheus metrics.
- Log JSON đã ghi thêm exception/stack info khi có lỗi.
- Runtime config validation cho các secret bắt buộc như `OPENAI_API_KEY` và `JWT_SECRET_KEY`.
- API key protection cho các endpoint nghiệp vụ bằng header `X-API-Key`; `health` và `metrics` vẫn public.
- Rule reload đã có error handling và logging khi rule config lỗi.
- Script kiểm tra Redis/Supabase đã tránh in secret trực tiếp và xử lý lỗi kết nối rõ hơn.
- Các API chính:
  - `GET /api/v1/health`
  - `POST /api/v1/predict`
  - `GET /api/v1/alerts`
  - `GET /api/v1/alerts/{id}`
  - `PATCH /api/v1/alerts/{id}/status`
  - `GET /api/v1/rules`
  - `POST /api/v1/rules/reload`
  - `GET /api/v1/metrics`

## 2. Phần ML Còn Cần Làm

Mục tiêu: thay mock ML bằng mô hình thật.

ML cần làm:

- Chuẩn bị dataset synthetic/public.
- Feature engineering.
- Train model thật, ví dụ:
  - Logistic Regression baseline.
  - XGBoost hoặc LightGBM làm model chính.
- Evaluate model bằng các metric:
  - precision
  - recall
  - F1
  - PR-AUC
  - ROC-AUC
  - false positive rate
- Tạo SHAP/top feature output.
- Serialize model artifact và preprocessor.

Đầu ra ML cần cung cấp cho backend:

```text
risk_score: float trong khoảng [0, 1]
top_features: list feature đóng góp nhiều nhất
model_version: string
```

Ví dụ output:

```json
{
  "risk_score": 0.83,
  "top_features": [
    {
      "name": "amount_to_sender_balance_ratio",
      "value": 0.76,
      "contribution": 0.21
    }
  ],
  "model_version": "xgboost-v1"
}
```

Cách gắn vào backend:

- Backend hiện đã có interface `ModelPredictor`.
- ML team chỉ cần implement `RealModelPredictor`.
- `RealModelPredictor` load model artifact và preprocessor.
- Output phải cùng format với `MockModelPredictor`.
- Sau đó đổi factory từ mock predictor sang real predictor.

Các file backend liên quan:

```text
backend/app/ml/predictor.py
backend/app/ml/mock_predictor.py
backend/app/ml/factory.py
```

## 3. Phần Frontend Còn Cần Làm

Mục tiêu: xây dựng dashboard cho Compliance Officer.

Các màn hình/module gợi ý:

- **Dashboard tổng quan**
  - Số lượng alert.
  - Tỷ lệ HIGH/CRITICAL.
  - Trạng thái hệ thống cơ bản.

- **Alert List**
  - Danh sách alert.
  - Filter theo status/risk level.

- **Alert Detail**
  - Risk score.
  - Risk level.
  - Triggered rules.
  - Top features.
  - LLM explanation.
  - Nút `Dismiss` và `Escalate`.

- **Prediction Demo**
  - Form nhập transaction mẫu.
  - Gọi `/api/v1/predict`.
  - Hiển thị kết quả scoring.

- **Rules View**
  - Hiển thị rule config đang active.
  - Có thể thêm reload rule sau nếu cần.

Backend endpoints frontend sẽ dùng:

```text
POST /api/v1/predict
GET /api/v1/alerts
GET /api/v1/alerts/{id}
PATCH /api/v1/alerts/{id}/status
GET /api/v1/rules
GET /api/v1/health
GET /api/v1/metrics
```

## 4. Docker Và Deployment

Docker chưa cần làm ngay.

Nên làm Docker khi:

- Backend đã ổn định.
- ML model thật đã được tích hợp.
- Frontend đã có bản demo.
- Cần demo/handover cho mentor hoặc người khác chạy bằng một lệnh.
- Cần chạy Redis ổn định cho idempotency runtime.

Redis hiện tại có thể chưa cần nếu `.env` để:

```env
IDEMPOTENCY_STORE=in_memory
```

Khi muốn dùng Redis thật, đổi `.env`:

```env
IDEMPOTENCY_STORE=redis
REDIS_URL=redis://localhost:6379/0
```

Lưu ý: flow idempotency hiện đã dùng cơ chế atomic reserve key trước khi chạy rule engine, ML predictor và tạo alert. Với Redis, cơ chế này dùng thao tác kiểu `SET NX`; với in-memory, cơ chế này an toàn trong phạm vi một process backend.

Có thể chạy riêng Redis bằng Docker trước khi làm Docker Compose:

```powershell
docker run --name anomalyx-redis -p 6379:6379 -d redis:7-alpine
python backend/scripts/check_redis.py
```

Nếu đã tạo container rồi nhưng đang stop:

```powershell
docker start anomalyx-redis
```

Dừng Redis:

```powershell
docker stop anomalyx-redis
```

Docker cần có:

- Backend Dockerfile.
- `docker-compose.yml`.
- Service backend.
- Service Redis.
- Không cần Postgres vì đã dùng Supabase.

Lệnh demo dự kiến:

```powershell
docker compose up --build
```

## 5. API Hardening Còn Cần Làm

Các việc nên làm sau khi frontend/ML bắt đầu ổn:

- Hoàn thiện authentication: hiện đã có `X-API-Key` guard cơ bản cho `predict`, `alerts`, `rules`; nếu cần phân quyền/user session thì nâng cấp sang JWT hoặc API key validation có danh sách key hợp lệ.
- Thêm CORS config cho frontend.
- Thêm error response format thống nhất.
- Quyết định response chuẩn cho trường hợp idempotency key đang được xử lý quá lâu.
- Thêm pagination cho `GET /api/v1/alerts`.
- Thêm filter theo ngày, status, risk level.
- Persist prediction logs.
- Persist review labels.

## 6. Testing Còn Cần Làm

Hiện backend đã có unit tests cho các phần chính, bao gồm regression test cho concurrent idempotency để đảm bảo hai request cùng key không tạo duplicate alert.

Đã validate gần nhất:

```powershell
$env:OPENAI_API_KEY='test-openai-key'; $env:JWT_SECRET_KEY='test-jwt-secret'; python -m pytest backend/tests
```

Kết quả: `27 passed`.

Vẫn nên làm thêm:

- Integration test với Redis thật cho atomic idempotency `SET NX`.
- Integration test với Supabase.
- Contract test từ OpenAPI.
- Load test cho `/predict`.
- E2E test:

```text
predict transaction -> create alert -> generate explanation -> update status
```

- Frontend tests sau khi có frontend.
- ML validation tests sau khi có model thật.
