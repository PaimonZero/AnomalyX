import assert from "node:assert/strict";
import test from "node:test";

import { parseMonitoringMetrics } from "./prometheus-parser.ts";

const sampleMetrics = `
anomalyx_http_requests_total{method="GET",path="/api/v1/health",status_code="200"} 8
anomalyx_http_requests_total{method="POST",path="/api/v1/predict",status_code="201"} 12
anomalyx_http_requests_total{method="POST",path="/api/v1/predict",status_code="422"} 3
anomalyx_http_requests_total{method="GET",path="/api/v1/alerts",status_code="500"} 1
anomalyx_http_request_duration_seconds_bucket{method="POST",path="/api/v1/predict",le="0.005"} 0
anomalyx_http_request_duration_seconds_bucket{method="POST",path="/api/v1/predict",le="0.5"} 20
anomalyx_http_request_duration_seconds_bucket{method="POST",path="/api/v1/predict",le="+Inf"} 24
anomalyx_decisions_total{risk_level="LOW",is_flagged="false"} 10
anomalyx_decisions_total{risk_level="HIGH",is_flagged="true"} 6
anomalyx_decisions_total{risk_level="CRITICAL",is_flagged="true"} 2
anomalyx_rule_triggers_total{rule_id="R-STRUCT-01",severity="HIGH"} 4
anomalyx_rule_triggers_total{rule_id="R-VELO-01",severity="MEDIUM"} 2
anomalyx_llm_explanations_total{source="llm"} 5
anomalyx_llm_explanations_total{source="template"} 1
anomalyx_llm_explanation_duration_seconds_bucket{source="llm",le="2.5"} 5
anomalyx_llm_explanation_duration_seconds_bucket{source="llm",le="+Inf"} 6
anomalyx_alerts_total 8
anomalyx_llm_fallback_total 1
anomalyx_model_drift_placeholder 0
`;

test("parseMonitoringMetrics maps backend Prometheus text to MonitoringMetrics", () => {
  const metrics = parseMonitoringMetrics(sampleMetrics);

  assert.equal(metrics.requestsTotal, 24);
  assert.equal(metrics.requestSuccessRate, 83.3);
  assert.equal(metrics.requestP95Ms, 500);
  assert.deepEqual(metrics.httpStatuses, { "2xx": 20, "4xx": 3, "5xx": 1 });
  assert.deepEqual(metrics.decisions, { LOW: 10, MEDIUM: 0, HIGH: 6, CRITICAL: 2 });
  assert.equal(metrics.alertsTotal, 8);
  assert.deepEqual(metrics.ruleTriggers, [
    { id: "R-STRUCT-01", severity: "HIGH", count: 4 },
    { id: "R-VELO-01", severity: "MEDIUM", count: 2 },
  ]);
  assert.deepEqual(metrics.explanationOutcomes, { llm: 5, template: 1 });
  assert.equal(metrics.explanationP95Ms, 2500);
  assert.equal(metrics.fallbackTotal, 1);
  assert.equal(metrics.driftPlaceholder, 0);
});

test("parseMonitoringMetrics aggregates duplicate rule trigger series by rule id", () => {
  const metrics = parseMonitoringMetrics(`
anomalyx_rule_triggers_total{rule_id="R-STRUCT-01",severity="HIGH",source="predict"} 3
anomalyx_rule_triggers_total{rule_id="R-STRUCT-01",severity="HIGH",source="batch"} 4
anomalyx_rule_triggers_total{rule_id="R-VELO-01",severity="MEDIUM",source="predict"} 2
`);

  assert.deepEqual(metrics.ruleTriggers, [
    { id: "R-STRUCT-01", severity: "HIGH", count: 7 },
    { id: "R-VELO-01", severity: "MEDIUM", count: 2 },
  ]);
});

test("parseMonitoringMetrics sorts scrambled histogram buckets", () => {
  const metrics = parseMonitoringMetrics(`
anomalyx_http_request_duration_seconds_bucket{le="1"} 20
anomalyx_http_request_duration_seconds_bucket{le="0.1"} 5
anomalyx_http_request_duration_seconds_bucket{le="+Inf"} 20
anomalyx_http_request_duration_seconds_bucket{le="0.5"} 18
`);

  assert.equal(metrics.requestP95Ms, 1000);
  assert.deepEqual(metrics.latencyTrend, [
    { label: "100ms", value: 5 },
    { label: "500ms", value: 18 },
    { label: "1000ms", value: 20 },
  ]);
});
