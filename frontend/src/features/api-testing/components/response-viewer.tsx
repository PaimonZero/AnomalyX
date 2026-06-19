import { Check, Clipboard, Clock3, FileJson, Files, Radio } from "lucide-react";
import { useState } from "react";

import { RiskBadge } from "@/features/alerts/components/alert-badges";
import type { ApiTestResponse } from "@/features/api-testing/types";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import type { ApiErrorEnvelope, PredictionResponse } from "@/shared/types/api";

interface ResponseViewerProps {
  response: ApiTestResponse | null;
  loading: boolean;
  onCopied: () => void;
}

type ResponseTab = "body" | "headers" | "raw";

function isErrorEnvelope(value: unknown): value is ApiErrorEnvelope {
  return typeof value === "object" && value !== null && "error" in value;
}

function isPrediction(value: unknown): value is PredictionResponse {
  return typeof value === "object" && value !== null && "risk_score" in value && "risk_level" in value && "is_flagged" in value;
}

export function ResponseViewer({ loading, onCopied, response }: ResponseViewerProps) {
  const [tab, setTab] = useState<ResponseTab>("body");

  const copyResponse = async () => {
    if (!response) return;
    await navigator.clipboard.writeText(response.raw);
    onCopied();
  };

  return (
    <section className="response-viewer">
      <div className="api-panel-heading response-heading">
        <div><span>Response</span><small>{response ? "Live API result" : "No request sent yet"}</small></div>
        {response ? (
          <div className="response-meta">
            <Badge tone={response.status < 300 ? "success" : response.status === 401 ? "warning" : "critical"}>{response.status} {response.statusText}</Badge>
            <span><Clock3 size={12} /> {response.latencyMs} ms</span>
            <span>{response.size}</span>
            <Button variant="ghost" size="sm" onClick={() => void copyResponse()}><Clipboard size={13} /> Copy</Button>
          </div>
        ) : null}
      </div>

      {loading ? (
        <div className="response-loading">
          <span /><span /><span /><span /><span />
        </div>
      ) : !response ? (
        <div className="response-empty">
          <Radio size={28} />
          <strong>Ready for a response</strong>
          <p>Edit the transaction payload, then send it to the prediction endpoint.</p>
        </div>
      ) : (
        <>
          <div className="response-tabs" role="tablist">
            <button className={tab === "body" ? "active" : ""} onClick={() => setTab("body")}><FileJson size={13} /> Body</button>
            <button className={tab === "headers" ? "active" : ""} onClick={() => setTab("headers")}><Files size={13} /> Headers</button>
            <button className={tab === "raw" ? "active" : ""} onClick={() => setTab("raw")}><Radio size={13} /> Raw</button>
          </div>

          <div className="response-content">
            {tab === "headers" ? (
              <dl className="response-headers">
                {Object.entries(response.headers).map(([key, value]) => <div key={key}><dt>{key}</dt><dd>{value}</dd></div>)}
              </dl>
            ) : tab === "raw" ? (
              <pre className="response-code">{response.raw}</pre>
            ) : isErrorEnvelope(response.body) ? (
              <div className="error-envelope">
                <Badge tone="critical">{response.body.error.code}</Badge>
                <h3>{response.body.error.message}</h3>
                <details>
                  <summary>Error details</summary>
                  <pre>{JSON.stringify(response.body.error.details, null, 2)}</pre>
                </details>
                {response.status === 401 ? <p>Check the shared bearer token in the sidebar.</p> : null}
              </div>
            ) : isPrediction(response.body) ? (
              <div className="prediction-response">
                <div className="prediction-summary">
                  <div><span>Risk score</span><strong>{response.body.risk_score.toFixed(2)}</strong></div>
                  <RiskBadge level={response.body.risk_level} />
                  <Badge tone={response.body.is_flagged ? "critical" : "success"}>{response.body.is_flagged ? "FLAGGED" : "PASSED"}</Badge>
                  {response.body.alert_id ? <code>{response.body.alert_id}</code> : null}
                </div>
                <div className="prediction-evidence">
                  <section>
                    <h3>Triggered rules</h3>
                    {response.body.triggered_rules.length ? response.body.triggered_rules.map((rule) => <div key={rule.id}><code>{rule.id}</code><Badge tone="high">{rule.severity}</Badge></div>) : <p>No rules triggered.</p>}
                  </section>
                  <section>
                    <h3>Top features</h3>
                    {response.body.top_features.map((feature) => <div key={feature.name}><code>{feature.name}</code><span>{String(feature.value)}</span><strong>{feature.contribution?.toFixed(2) ?? "—"}</strong></div>)}
                  </section>
                </div>
                <div className="async-note"><Check size={14} /> {response.body.explanation ?? "Explanation is being generated asynchronously…"}</div>
                
              </div>
            ) : (
              <pre className="response-code">{response.raw}</pre>
            )}
          </div>
        </>
      )}
    </section>
  );
}
