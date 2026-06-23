from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram


REQUEST_COUNT = Counter(
    "anomalyx_http_requests_total",
    "Total HTTP requests.",
    ["method", "path", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "anomalyx_http_request_duration_seconds",
    "HTTP request latency in seconds.",
    ["method", "path"],
)

DECISION_COUNT = Counter(
    "anomalyx_decisions_total",
    "Total prediction decisions.",
    ["risk_level", "is_flagged"],
)

RULE_TRIGGER_COUNT = Counter(
    "anomalyx_rule_triggers_total",
    "Total triggered rule occurrences.",
    ["rule_id", "severity"],
)

LLM_EXPLANATION_COUNT = Counter(
    "anomalyx_llm_explanations_total",
    "Total LLM explanation outcomes.",
    ["source"],
)

LLM_LATENCY = Histogram(
    "anomalyx_llm_explanation_duration_seconds",
    "LLM explanation latency in seconds.",
    ["source"],
)

ALERT_COUNT = Counter(
    "anomalyx_alerts_total",
    "Total flagged predictions that created alerts.",
)

LLM_FALLBACK_COUNT = Counter(
    "anomalyx_llm_fallback_total",
    "Total explanation fallbacks to the deterministic template.",
)

EXPLANATION_CACHE_HIT = Counter(
    "anomalyx_explanation_cache_hits_total",
    "Total explanation cache hits.",
)

MODEL_DRIFT_PLACEHOLDER = Gauge(
    "anomalyx_model_drift_placeholder",
    "Placeholder drift indicator until real drift detection is implemented.",
)
MODEL_DRIFT_PLACEHOLDER.set(0)

MODEL_DRIFT_PSI = Gauge(
    "anomalyx_model_drift_psi",
    "PSI-based model score drift.",
)
MODEL_DRIFT_PSI.set(0.0)

FEATURE_DRIFT_PSI = Gauge(
    "anomalyx_feature_drift_psi",
    "Feature-level drift index.",
)
FEATURE_DRIFT_PSI.set(0.0)


def record_prediction(risk_level: str, is_flagged: bool, triggered_rules: list) -> None:
    DECISION_COUNT.labels(risk_level=risk_level, is_flagged=str(is_flagged).lower()).inc()
    if is_flagged:
        ALERT_COUNT.inc()
    for rule in triggered_rules:
        RULE_TRIGGER_COUNT.labels(rule_id=rule.id, severity=rule.severity.value).inc()


def record_explanation_result(source: str) -> None:
    LLM_EXPLANATION_COUNT.labels(source=source).inc()
    if source == "template":
        LLM_FALLBACK_COUNT.inc()
    elif source == "cache":
        EXPLANATION_CACHE_HIT.inc()



def observe_explanation_latency(source: str, latency_seconds: float) -> None:
    LLM_LATENCY.labels(source=source).observe(latency_seconds)


def set_model_drift_placeholder(value: float = 0.0) -> None:
    MODEL_DRIFT_PLACEHOLDER.set(value)
    MODEL_DRIFT_PSI.set(value)


def set_model_drift_psi(value: float) -> None:
    MODEL_DRIFT_PSI.set(value)
    MODEL_DRIFT_PLACEHOLDER.set(value)


def set_feature_drift_psi(value: float) -> None:
    FEATURE_DRIFT_PSI.set(value)
