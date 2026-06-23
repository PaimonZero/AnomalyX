# Plan: Sửa các Gaps còn lại & Bổ sung Tests

Kế hoạch triển khai 4 điểm thiếu sót đã xác định trong audit, cùng bộ test kiểm chứng từng phần thay đổi đảm bảo đúng mục tiêu PRD/TDD.

## User Review Required

> [!IMPORTANT]
> Kế hoạch này thay đổi **Feature Service** — đường dẫn chính tính toán feature cho cả Rule Engine lẫn ML predictor. Mọi thay đổi ở đây ảnh hưởng trực tiếp đến kết quả scoring.

> [!WARNING]
> **Redis rolling aggregates** hiện dùng constant proxy. Sau khi triển khai, các giao dịch lần đầu (cold-start sender) sẽ thấy velocity features = 0 thay vì proxy cũ. Điều này có thể **thay đổi output** của rule engine cho một số test case. Tuy nhiên đây là hành vi đúng theo TDD §3.2.

## Open Questions

1. **Scope Geo/Device:** TDD §4.3 ghi rõ "partial implementation" — bạn muốn triển khai **full historical profile** (lưu device/location history per sender vào Redis) hay chỉ cần **stub có test** chứng minh khi có data thì pipeline hoạt động đúng?
2. **Drift metric:** Bạn muốn PSI/KS thực sự tính trên distribution lưu trong model registry, hay chỉ cần **functional placeholder** có gauge output thay đổi được theo API call (đủ cho demo W6)?

---

## Proposed Changes

### Component 1: Redis Rolling Aggregates (TDD §3.2, PRD §4.1.1)

**Mục tiêu:** Thay proxy constants trong `FeatureService` bằng Redis sliding-window counters thực tế cho mỗi `sender_id`. Cold-start senders fall back to neutral defaults + `has_history=false` indicator.

#### [NEW] [redis_aggregates.py](file:///i:/VinUni/1_vfs/AnomalyX/backend/app/features/redis_aggregates.py)

Tạo module `RedisAggregateService` quản lý per-sender rolling counters:

```python
# Sliding-window counters lưu trong Redis sorted sets keyed by sender_id
# Keys: anomalyx:agg:{sender_id}:txns (sorted set, score=timestamp)
#        anomalyx:agg:{sender_id}:receivers:{window} (HyperLogLog or set)
```

Các aggregate cần tính:
| Feature | Window | Redis structure | TDD ref |
|---|---|---|---|
| `tx_count_1h` / `tx_count_24h` | 1h, 24h | Sorted Set ZCOUNT | §3.1 Velocity |
| `sum_amount_1h` / `sum_amount_24h` | 1h, 24h | Sorted Set + member=amount | §3.1 Velocity |
| `distinct_receivers_1h` / `distinct_receivers_24h` | 1h, 24h | Set SCARD | §3.1 Counterparty |
| `count_just_below_threshold_24h` | 24h | Sorted Set filter | §3.1 Structuring |
| `rapid_inout_count_1h` | 1h | Counter based on in→out pattern | §3.1 Sequence |

API:
- `record_transaction(sender_id, receiver_id, amount, timestamp, channel)` — ghi transaction vào Redis
- `get_aggregates(sender_id, timestamp) -> dict` — trả về rolling features cho thời điểm hiện tại
- Cold-start: nếu sender chưa có history, trả về `{"has_history": False, "tx_count_1h": 0, ...}`

#### [MODIFY] [service.py](file:///i:/VinUni/1_vfs/AnomalyX/backend/app/features/service.py)

- Import `RedisAggregateService` 
- Trong `compute()`, gọi `get_aggregates(sender_id, timestamp)` để lấy real values
- Fallback về current proxy defaults khi `IDEMPOTENCY_STORE=in_memory` (no Redis available)
- Thêm `has_history` indicator vào feature dict
- **Record** transaction vào Redis sau khi compute (để sender tiếp theo thấy history)

#### [MODIFY] [xgb_predictor.py](file:///i:/VinUni/1_vfs/AnomalyX/backend/app/ml/xgb_predictor.py)

- Thay constant cold-start defaults (`tx_count_sender=1`, etc.) bằng values từ `RedisAggregateService`
- Nếu `has_history=False`, dùng neutral defaults (0 cho counters, amount cho totals)

#### [MODIFY] [engine.py](file:///i:/VinUni/1_vfs/AnomalyX/backend/app/rules/engine.py)

- Thêm vào `ALLOWED_CONTEXT_NAMES`: `has_history`, `tx_count_1h`, `tx_count_24h`, `sum_amount_24h`, `distinct_receivers_24h`, `count_just_below_threshold_24h`, `rapid_inout_count_1h`
- Giữ backward compatibility: proxy names vẫn hoạt động cho rules cũ

#### [MODIFY] [configs/rules.yaml](file:///i:/VinUni/1_vfs/AnomalyX/configs/rules.yaml)

- Cập nhật rules dùng real feature names thay vì `_proxy` suffix khi Redis available
- Giữ rules cũ nếu muốn backward compat, hoặc migrate sang tên mới

---

### Component 2: Explanation Cache (TDD §7.2)

**Mục tiêu:** Cache explanations theo fingerprint `(sorted triggered rules, bucketed top features)` để tránh gọi LLM lặp lại cho các pattern giống nhau.

#### [NEW] [explanation_cache.py](file:///i:/VinUni/1_vfs/AnomalyX/backend/app/llm/explanation_cache.py)

```python
class ExplanationCache:
    """Cache explanations by (rule_set, bucketed_features) fingerprint."""
    def cache_key(alert: Alert) -> str:
        # Sort rule IDs + bucket top feature contributions
        ...
    def get(key: str) -> ExplanationResult | None: ...
    def set(key: str, result: ExplanationResult, ttl: int): ...
```

- Implementation: Redis-backed (`HSET` with TTL) khi Redis available, in-memory `dict` khi không
- Cache TTL: configurable, default 1 hour
- Fingerprint = hash of `sorted(rule_ids) + bucketed(top_feature_names + round(contributions, 1))`

#### [MODIFY] [explainer.py](file:///i:/VinUni/1_vfs/AnomalyX/backend/app/llm/explainer.py)

- Trong `OpenAIAlertExplainer.explain()`: kiểm tra cache trước khi gọi OpenAI
- Sau khi nhận response thành công từ LLM: ghi vào cache
- Cache hit → trả về `ExplanationResult(text=cached, source="cache")`

#### [MODIFY] [prediction_service.py](file:///i:/VinUni/1_vfs/AnomalyX/backend/app/services/prediction_service.py)

- Trong `explain_alert()`: log cache hit/miss vào metrics
- Thêm `"cache"` vào list source types cho `record_explanation_result()`

#### [MODIFY] [metrics.py](file:///i:/VinUni/1_vfs/AnomalyX/backend/app/core/metrics.py)

- Thêm `EXPLANATION_CACHE_HIT` counter
- Cập nhật `record_explanation_result` hỗ trợ source `"cache"`

---

### Component 3: Geo/Device Anomaly (TDD §4.3, PRD §7.3)

**Mục tiêu:** Triển khai so sánh device/location của transaction hiện tại với lịch sử per-sender lưu trong Redis, thay vì luôn trả `False`.

#### [MODIFY] [redis_aggregates.py](file:///i:/VinUni/1_vfs/AnomalyX/backend/app/features/redis_aggregates.py)

Thêm vào `RedisAggregateService`:
- `record_device_location(sender_id, device_id, country, region, timestamp)` — ghi device/geo evidence
- `get_geo_device_features(sender_id, device_id, country, region) -> dict`:
  - `new_device`: True nếu `device_id` chưa từng thấy cho sender
  - `geo_anomaly`: True nếu `country` hoặc `region` khác với top-1 historical pattern
  - `impossible_travel`: True nếu transaction trước < 1h nhưng country khác (simplified)

#### [MODIFY] [service.py](file:///i:/VinUni/1_vfs/AnomalyX/backend/app/features/service.py)

- Khi `geo_device_evidence_available=True` và Redis available: gọi `get_geo_device_features()` thay vì hardcode `False`
- Cold-start (no history): vẫn trả `False` (đúng behavior — chưa có baseline)

---

### Component 4: Drift Metrics (TDD §8, PRD §4.1.6)

**Mục tiêu:** Thay placeholder gauge bằng PSI (Population Stability Index) thực sự tính trên distribution score gần nhất vs baseline.

#### [NEW] [drift.py](file:///i:/VinUni/1_vfs/AnomalyX/backend/app/core/drift.py)

```python
class ScoreDriftDetector:
    """Track score distribution drift using PSI."""
    def __init__(self, baseline_bins: int = 10):
        self._baseline: list[float] = []  # baseline scores
        self._recent: list[float] = []    # recent window scores
    
    def record_score(self, score: float): ...
    def set_baseline(self, scores: list[float]): ...
    def compute_psi(self) -> float: ...
```

- Baseline: loaded from model registry hoặc set qua API
- Recent window: last N predictions (configurable, default 1000)
- PSI > 0.2 → significant drift → update gauge + log warning

#### [MODIFY] [metrics.py](file:///i:/VinUni/1_vfs/AnomalyX/backend/app/core/metrics.py)

- Thay `MODEL_DRIFT_PLACEHOLDER` bằng `MODEL_DRIFT_PSI` gauge có giá trị thực
- Thêm `FEATURE_DRIFT_PSI` gauge cho feature-level drift

#### [MODIFY] [prediction_service.py](file:///i:/VinUni/1_vfs/AnomalyX/backend/app/services/prediction_service.py)

- Sau mỗi prediction: gọi `drift_detector.record_score(risk_score)`
- Periodically (mỗi N predictions): compute PSI và update gauge

#### [NEW] [routes/drift.py](file:///i:/VinUni/1_vfs/AnomalyX/backend/app/api/v1/routes/drift.py) *(optional)*

- `POST /api/v1/drift/baseline` — set baseline distribution (ML Engineer)
- `GET /api/v1/drift/status` — current PSI values

---

## Verification Plan

### Automated Tests

Tất cả tests mới phải pass khi chạy:
```bash
py -m pytest backend/tests -q
```

#### Test Group 1: Redis Aggregates

File: `backend/tests/test_redis_aggregates.py`

| Test case | Mục đích | PRD/TDD ref |
|---|---|---|
| `test_record_and_get_tx_count` | Record 5 txns, verify `tx_count_1h=5` | TDD §3.1 |
| `test_sum_amount_window` | Record txns, verify `sum_amount_1h` chính xác | TDD §3.1 |
| `test_distinct_receivers` | Record txns to 3 different receivers, verify `distinct_receivers_1h=3` | TDD §3.1 |
| `test_count_just_below_threshold` | Record 4 txns just below 400M VND, verify count=4 | PRD §7.3 Structuring |
| `test_cold_start_returns_defaults` | New sender has `has_history=False`, all counters=0 | TDD §3.2 |
| `test_window_expiry` | Txns older than window are excluded | TDD §3.2 |
| `test_feature_service_uses_redis` | `FeatureService.compute()` returns real aggregates from Redis | Integration |

#### Test Group 2: Explanation Cache

File: `backend/tests/test_explanation_cache.py`

| Test case | Mục đích | PRD/TDD ref |
|---|---|---|
| `test_cache_miss_calls_llm` | First call → miss → calls LLM | TDD §7.2 |
| `test_cache_hit_skips_llm` | Same rule/feature pattern → hit → returns cached | TDD §7.2 |
| `test_different_rules_different_cache` | Different rule sets → different cache keys | TDD §7.2 |
| `test_cache_ttl_expiry` | Cached entry expires after TTL | TDD §7.2 |
| `test_template_fallback_not_cached` | Template results are NOT cached | Correctness |

#### Test Group 3: Geo/Device Anomaly

File: `backend/tests/test_geo_device.py`

| Test case | Mục đích | PRD/TDD ref |
|---|---|---|
| `test_new_device_detected` | Unknown device_id → `new_device=True` | TDD §4.3 R-GEO-01 |
| `test_known_device_no_flag` | Known device_id → `new_device=False` | TDD §4.3 |
| `test_geo_anomaly_different_country` | Transaction from unusual country → `geo_anomaly=True` | PRD §7.3 |
| `test_cold_start_no_anomaly` | No history → all geo/device flags = `False` | TDD §4.3 |
| `test_rule_geo_01_fires` | With anomaly features, R-GEO-01 triggers | PRD §6.2 |

#### Test Group 4: Drift Detection

File: `backend/tests/test_drift.py`

| Test case | Mục đích | PRD/TDD ref |
|---|---|---|
| `test_psi_zero_identical_distributions` | Same distribution → PSI ≈ 0 | TDD §8 |
| `test_psi_high_shifted_distribution` | Shifted distribution → PSI > 0.2 | TDD §8 |
| `test_drift_gauge_updated` | After computing PSI, Prometheus gauge reflects value | PRD §4.1.6 |
| `test_record_score_accumulates` | Recording scores adds to recent window | Correctness |

#### Test Group 5: XGBPredictor Integration

File: `backend/tests/test_xgb_predictor.py`

| Test case | Mục đích | PRD/TDD ref |
|---|---|---|
| `test_feature_mapping_26_columns` | `_compute_features()` produces exactly the 26 model columns | TDD §5.6 |
| `test_prediction_contract` | Returns `ModelPrediction` with score ∈ [0,1] and model_version | TDD §5.6 |
| `test_shap_fallback_on_error` | SHAP failure → empty `top_features` without crash | TDD §5.5 |
| `test_cold_start_features` | With `has_history=False` → neutral defaults | TDD §3.2 |

#### Regression

Chạy toàn bộ test suite hiện có (66 tests) để đảm bảo không bị regression:
```bash
py -m pytest backend/tests -q
```

### Manual Verification

1. Khởi động backend với `ALERT_REPOSITORY=postgres`, `IDEMPOTENCY_STORE=redis`:
   - Submit 5 transactions cùng `sender_id` qua Swagger UI
   - Verify Redis keys được tạo (`anomalyx:agg:{sender_id}:*`)
   - Verify transaction thứ 5 có velocity features khác 0
2. Submit 2 transactions flagged cùng rule pattern → verify explanation cache hit ở lần 2
3. Submit transaction với `device_id` mới → verify `new_device=True` trong features
4. Kiểm tra `/metrics` endpoint → verify `anomalyx_model_drift_psi` gauge có giá trị

### Test Coverage Target

```bash
py -m pytest --cov=app backend/tests
```
Mục tiêu: **≥ 70%** coverage trên core modules (TDD §10).
