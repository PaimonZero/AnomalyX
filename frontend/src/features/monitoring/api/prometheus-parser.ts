import type { MonitoringMetrics } from "@/features/monitoring/types";

type MetricLabels = Record<string, string>;

interface MetricSample {
  name: string;
  labels: MetricLabels;
  value: number;
}

const riskLevels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"] as const;

function parseLabels(rawLabels = ""): MetricLabels {
  const labels: MetricLabels = {};
  const labelPattern = /([a-zA-Z_][\w]*)="((?:\\.|[^"])*)"/g;
  let match: RegExpExecArray | null;

  while ((match = labelPattern.exec(rawLabels)) !== null) {
    labels[match[1]] = match[2].replace(/\\"/g, "\"").replace(/\\\\/g, "\\");
  }

  return labels;
}

function parseSamples(metricsText: string): MetricSample[] {
  return metricsText
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("#"))
    .flatMap((line) => {
      const match = /^([a-zA-Z_:][\w:]*)(?:\{([^}]*)\})?\s+([-+]?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?|[-+]?Inf)$/i.exec(line);
      if (!match) return [];
      const value = Number(match[3]);
      if (!Number.isFinite(value)) return [];
      return [{ name: match[1], labels: parseLabels(match[2]), value }];
    });
}

function sumMetric(samples: MetricSample[], name: string, predicate: (labels: MetricLabels) => boolean = () => true) {
  return samples
    .filter((sample) => sample.name === name && predicate(sample.labels))
    .reduce((sum, sample) => sum + sample.value, 0);
}

function estimateHistogramP95Ms(samples: MetricSample[], bucketName: string, labelFilter: (labels: MetricLabels) => boolean = () => true) {
  const buckets = new Map<number, number>();
  let total = 0;

  for (const sample of samples) {
    if (sample.name !== bucketName || !labelFilter(sample.labels)) continue;
    const rawLe = sample.labels.le;
    if (!rawLe) continue;
    if (rawLe === "+Inf") {
      total += sample.value;
      continue;
    }
    const upperBound = Number(rawLe);
    if (!Number.isFinite(upperBound)) continue;
    buckets.set(upperBound, (buckets.get(upperBound) ?? 0) + sample.value);
  }

  const sortedBuckets = [...buckets.entries()].sort(([left], [right]) => left - right);
  if (!sortedBuckets.length) return 0;

  const threshold = total > 0 ? total * 0.95 : sortedBuckets.at(-1)![1] * 0.95;
  const matched = sortedBuckets.find(([, cumulative]) => cumulative >= threshold) ?? sortedBuckets.at(-1)!;
  return Math.round(matched[0] * 1000);
}

function groupStatus(statusCode: string) {
  if (statusCode.startsWith("2") || statusCode.startsWith("3")) return "2xx";
  if (statusCode.startsWith("4")) return "4xx";
  if (statusCode.startsWith("5")) return "5xx";
  return null;
}

export function parseMonitoringMetrics(metricsText: string): MonitoringMetrics {
  const samples = parseSamples(metricsText);
  const httpStatuses: MonitoringMetrics["httpStatuses"] = { "2xx": 0, "4xx": 0, "5xx": 0 };
  const decisions: MonitoringMetrics["decisions"] = { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 };

  for (const sample of samples) {
    if (sample.name === "anomalyx_http_requests_total") {
      const grouped = groupStatus(sample.labels.status_code ?? "");
      if (grouped) httpStatuses[grouped] += sample.value;
    }

    if (sample.name === "anomalyx_decisions_total") {
      const level = sample.labels.risk_level;
      if (riskLevels.some((riskLevel) => riskLevel === level)) {
        decisions[level as keyof MonitoringMetrics["decisions"]] += sample.value;
      }
    }
  }

  const requestsTotal = httpStatuses["2xx"] + httpStatuses["4xx"] + httpStatuses["5xx"];
  const successRate = requestsTotal ? Number(((httpStatuses["2xx"] / requestsTotal) * 100).toFixed(1)) : 0;
  const requestP95Ms = estimateHistogramP95Ms(samples, "anomalyx_http_request_duration_seconds_bucket");
  const explanationP95Ms = estimateHistogramP95Ms(samples, "anomalyx_llm_explanation_duration_seconds_bucket");

  const ruleTriggerMap = new Map<string, MonitoringMetrics["ruleTriggers"][number]>();
  for (const sample of samples) {
    if (sample.name !== "anomalyx_rule_triggers_total") continue;
    const id = sample.labels.rule_id ?? "unknown_rule";
    const severity = sample.labels.severity === "MEDIUM" ? "MEDIUM" : "HIGH";
    const existing = ruleTriggerMap.get(id);
    if (existing) {
      existing.count += sample.value;
      if (severity === "HIGH") existing.severity = "HIGH";
    } else {
      ruleTriggerMap.set(id, { id, severity, count: sample.value });
    }
  }

  const ruleTriggers = [...ruleTriggerMap.values()]
    .sort((left, right) => right.count - left.count)
    .slice(0, 8);

  return {
    requestsTotal,
    requestSuccessRate: successRate,
    requestP95Ms,
    alertsTotal: sumMetric(samples, "anomalyx_alerts_total"),
    decisions,
    httpStatuses,
    ruleTriggers,
    explanationOutcomes: {
      llm: sumMetric(samples, "anomalyx_llm_explanations_total", (labels) => labels.source === "llm"),
      template: sumMetric(samples, "anomalyx_llm_explanations_total", (labels) => labels.source === "template"),
    },
    explanationP95Ms,
    fallbackTotal: sumMetric(samples, "anomalyx_llm_fallback_total"),
    driftPlaceholder: sumMetric(samples, "anomalyx_model_drift_placeholder"),
    requestVolume: Object.entries(httpStatuses).map(([label, value]) => ({ label, value })),
    latencyTrend: samples
      .filter((sample) => sample.name === "anomalyx_http_request_duration_seconds_bucket" && sample.labels.le !== "+Inf")
      .map((sample) => ({ sample, upperBound: Number(sample.labels.le) }))
      .filter(({ upperBound }) => Number.isFinite(upperBound))
      .sort((left, right) => left.upperBound - right.upperBound)
      .slice(0, 12)
      .map(({ sample, upperBound }) => ({ label: `${upperBound * 1000}ms`, value: sample.value })),
    scrapedAt: new Date().toISOString(),
  };
}
