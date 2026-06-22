import assert from "node:assert/strict";
import test from "node:test";

import { buildIntegrationSample } from "./integration-sample.ts";

test("buildIntegrationSample uses the configured API base URL and entered bearer token", () => {
  const sample = buildIntegrationSample({
    apiBaseUrl: "http://localhost:8000/api/v1",
    body: "{\n  \"transaction_id\": \"tx_001\"\n}",
    endpointPath: "/api/v1/predict",
    token: "demo-token",
  });

  assert.equal(sample.endpoint, "http://localhost:8000/api/v1/predict");
  assert.match(sample.curl, /Authorization: Bearer demo-token/);
  assert.match(sample.curl, /http:\/\/localhost:8000\/api\/v1\/predict/);
});

test("buildIntegrationSample falls back to AUTH_TOKEN placeholder when token is empty", () => {
  const sample = buildIntegrationSample({
    apiBaseUrl: "/api/v1",
    body: "{}",
    endpointPath: "/api/v1/predict",
    token: "  ",
  });

  assert.equal(sample.endpoint, "/api/v1/predict");
  assert.match(sample.curl, /Authorization: Bearer <AUTH_TOKEN>/);
});

test("buildIntegrationSample can generate the batch score endpoint", () => {
  const sample = buildIntegrationSample({
    apiBaseUrl: "https://aml.example.com/api/v1",
    body: "{\n  \"batch_id\": \"demo\",\n  \"transactions\": []\n}",
    endpointPath: "/api/v1/batch-score",
    token: "batch-token",
  });

  assert.equal(sample.endpoint, "https://aml.example.com/api/v1/batch-score");
  assert.match(sample.curl, /"batch_id": "demo"/);
});
