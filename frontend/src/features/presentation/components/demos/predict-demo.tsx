import { apiRequest } from "@/shared/api/client";
import type { PredictionResponse, TransactionRequest } from "@/shared/types/api";
import { useMutation } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle2, Loader2, Send } from "lucide-react";
import { useState } from "react";
import type { Language } from "../../types";

const SAMPLE_TX: TransactionRequest = {
  transaction_id: "tx_demo_001",
  sender_id: "h:sender001",
  receiver_id: "h:receiver001",
  sender_balance: 500_000_000,
  receiver_balance: 200_000,
  amount: 380_000_000,
  currency: "VND",
  timestamp: new Date().toISOString(),
  channel: "TRANSFER",
};

const CHANNELS = ["PAYMENT", "TRANSFER", "CASH_OUT", "CASH_IN", "DEBIT"] as const;

const RISK_COLORS: Record<string, string> = {
  LOW: "var(--risk-low)",
  MEDIUM: "var(--risk-medium)",
  HIGH: "var(--risk-high)",
  CRITICAL: "var(--risk-critical)",
};

function usePredictMutation(token: string) {
  return useMutation({
    mutationFn: (body: TransactionRequest) =>
      apiRequest<PredictionResponse>("/predict", { method: "POST", token, body }),
  });
}

export function PredictDemo({ language, token }: { language: Language; token: string }) {
  const [form, setForm] = useState<TransactionRequest>({ ...SAMPLE_TX });
  const mutation = usePredictMutation(token);

  const update = (key: keyof TransactionRequest, value: string | number) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(form);
  };

  const labels = {
    title: language === "vi" ? "Dự đoán Giao dịch" : "Transaction Prediction",
    id: language === "vi" ? "Mã giao dịch" : "Transaction ID",
    sender: language === "vi" ? "Người gửi" : "Sender ID",
    receiver: language === "vi" ? "Người nhận" : "Receiver ID",
    amount: language === "vi" ? "Số tiền" : "Amount",
    currency: language === "vi" ? "Tiền tệ" : "Currency",
    channel: language === "vi" ? "Kênh" : "Channel",
    senderBal: language === "vi" ? "Số dư gửi" : "Sender Balance",
    receiverBal: language === "vi" ? "Số dư nhận" : "Receiver Balance",
    timestamp: language === "vi" ? "Thời gian" : "Timestamp",
    submit: language === "vi" ? "Gửi Dự đoán" : "Submit Prediction",
    result: language === "vi" ? "Kết quả" : "Result",
    riskScore: language === "vi" ? "Risk Score" : "Risk Score",
    riskLevel: language === "vi" ? "Mức độ rủi ro" : "Risk Level",
    modelVersion: language === "vi" ? "Model" : "Model",
    triggeredRules: language === "vi" ? "Rule được kích hoạt" : "Triggered Rules",
    topFeatures: language === "vi" ? "Top Features" : "Top Features",
    severity: language === "vi" ? "Mức độ" : "Severity",
    contribution: language === "vi" ? "Đóng góp" : "Contribution",
    error: language === "vi" ? "Lỗi kết nối backend. Khởi động với docker compose up." : "Backend unavailable. Start with docker compose up.",
  };

  return (
    <div className="predict-demo">
      <div className="predict-demo-form-panel">
        <h3>{labels.title}</h3>
        <form onSubmit={handleSubmit}>
          <div className="predict-demo-grid">
            <label>
              <span>{labels.id}</span>
              <input type="text" value={form.transaction_id} onChange={(e) => update("transaction_id", e.target.value)} />
            </label>
            <label>
              <span>{labels.sender}</span>
              <input type="text" value={form.sender_id} onChange={(e) => update("sender_id", e.target.value)} />
            </label>
            <label>
              <span>{labels.receiver}</span>
              <input type="text" value={form.receiver_id} onChange={(e) => update("receiver_id", e.target.value)} />
            </label>
            <label>
              <span>{labels.amount}</span>
              <input type="number" value={form.amount} onChange={(e) => update("amount", Number(e.target.value))} />
            </label>
            <label>
              <span>{labels.currency}</span>
              <input type="text" value={form.currency} onChange={(e) => update("currency", e.target.value)} />
            </label>
            <label>
              <span>{labels.channel}</span>
              <select value={form.channel} onChange={(e) => update("channel", e.target.value)}>
                {CHANNELS.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </label>
            <label>
              <span>{labels.senderBal}</span>
              <input type="number" value={form.sender_balance} onChange={(e) => update("sender_balance", Number(e.target.value))} />
            </label>
            <label>
              <span>{labels.receiverBal}</span>
              <input type="number" value={form.receiver_balance} onChange={(e) => update("receiver_balance", Number(e.target.value))} />
            </label>
          </div>
          <div className="predict-demo-actions">
            <button className="button button--primary" type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? <Loader2 size={16} className="spin" /> : <Send size={16} />}
              {labels.submit}
            </button>
          </div>
        </form>
      </div>

      <div className="predict-demo-result-panel">
        <h3>{labels.result}</h3>
        {mutation.isPending && (
          <div className="predict-demo-loading">
            <Loader2 size={24} className="spin" />
            <span>{language === "vi" ? "Đang xử lý..." : "Processing..."}</span>
          </div>
        )}
        {mutation.isError && (
          <div className="predict-demo-error">
            <AlertTriangle size={18} />
            <span>{labels.error}</span>
          </div>
        )}
        {mutation.isSuccess && mutation.data && (
          <div className="predict-demo-result">
            <div className="predict-demo-result-header">
              <div>
                <span className="predict-demo-label">{labels.riskScore}</span>
                <span className="predict-demo-score" style={{ color: RISK_COLORS[mutation.data.risk_level] || "inherit" }}>
                  {mutation.data.risk_score.toFixed(4)}
                </span>
              </div>
              <div>
                <span className="predict-demo-label">{labels.riskLevel}</span>
                <span className={`badge badge--${mutation.data.risk_level.toLowerCase() === "critical" ? "critical" : mutation.data.risk_level.toLowerCase() === "high" ? "high" : mutation.data.risk_level.toLowerCase() === "medium" ? "warning" : "success"}`}>
                  {mutation.data.risk_level}
                </span>
              </div>
              <div>
                <span className="predict-demo-label">{labels.modelVersion}</span>
                <span className="predict-demo-model">{mutation.data.model_version}</span>
              </div>
            </div>

            {mutation.data.triggered_rules.length > 0 && (
              <div className="predict-demo-section">
                <h4>{labels.triggeredRules}</h4>
                <table className="predict-demo-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>{labels.severity}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mutation.data.triggered_rules.map((r) => (
                      <tr key={r.id}>
                        <td className="mono">{r.id}</td>
                        <td>
                          <span className={`badge badge--${r.severity.toLowerCase() === "critical" ? "critical" : r.severity.toLowerCase() === "high" ? "high" : "neutral"}`}>
                            {r.severity}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {mutation.data.top_features.length > 0 && (
              <div className="predict-demo-section">
                <h4>{labels.topFeatures}</h4>
                <table className="predict-demo-table">
                  <thead>
                    <tr>
                      <th>Feature</th>
                      <th>Value</th>
                      <th>{labels.contribution}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mutation.data.top_features.map((f) => (
                      <tr key={f.name}>
                        <td className="mono">{f.name}</td>
                        <td className="mono">{typeof f.value === "number" ? f.value.toFixed(4) : String(f.value)}</td>
                        <td className="mono">{f.contribution != null ? f.contribution.toFixed(4) : "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {mutation.data.is_flagged && (
              <div className="predict-demo-flagged">
                <CheckCircle2 size={16} />
                <span>
                  {language === "vi"
                    ? `Alert đã được tạo${mutation.data.alert_id ? `: ${mutation.data.alert_id}` : ""}`
                    : `Alert created${mutation.data.alert_id ? `: ${mutation.data.alert_id}` : ""}`}
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
