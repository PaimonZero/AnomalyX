from __future__ import annotations

from prometheus_client import Counter, Histogram


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


def record_prediction(risk_level: str, is_flagged: bool, triggered_rules: list) -> None:
    DECISION_COUNT.labels(risk_level=risk_level, is_flagged=str(is_flagged).lower()).inc()
    for rule in triggered_rules:
        RULE_TRIGGER_COUNT.labels(rule_id=rule.id, severity=rule.severity.value).inc()
