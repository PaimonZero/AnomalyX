import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  Cpu,
  Database,
  FileText,
  FolderTree,
  Layers,
  Lightbulb,
  Server,
  Shield,
  Target,
  Workflow,
} from "lucide-react";
import type { Slide } from "../types";
import { AlertsDemo } from "../components/demos/alerts-demo";
import { ArchitectureDiagram } from "../components/demos/architecture-diagram";
import { HealthDemo } from "../components/demos/health-demo";
import { PredictDemo } from "../components/demos/predict-demo";
import { RulesDemo } from "../components/demos/rules-demo";
import { bilingual, IconBullet, Tag } from "./slide-helpers";

/* ──────────────── Slide definitions ──────────────── */

const slideDefinitions: Slide[] = [
  /* 1 — Title */
  {
    id: "title",
    layout: "title",
    background: "accent",
    content: bilingual(
      <>
        <div className="slide-brand-mark">AX</div>
        <h1 className="slide-title-text">AnomalyX</h1>
        <p className="slide-subtitle">
          Hệ thống phát hiện giao dịch bất thường AML
          <br />
          cho ví điện tử
        </p>
        <div className="slide-tag-row">
          <Tag>FastAPI</Tag>
          <Tag>React</Tag>
          <Tag>XGBoost</Tag>
          <Tag>LLM</Tag>
        </div>
      </>,
      <>
        <div className="slide-brand-mark">AX</div>
        <h1 className="slide-title-text">AnomalyX</h1>
        <p className="slide-subtitle">
          AML Transaction Anomaly Detection
          <br />
          for E-Wallets
        </p>
        <div className="slide-tag-row">
          <Tag>FastAPI</Tag>
          <Tag>React</Tag>
          <Tag>XGBoost</Tag>
          <Tag>LLM</Tag>
        </div>
      </>,
    ),
  },

  /* 2 — The Problem */
  {
    id: "problem",
    layout: "two-column",
    content: bilingual(
      <>
        <div>
          <h2 className="slide-heading">Vấn đề</h2>
          <p className="slide-lead">
            Rửa tiền là vấn nạn toàn cầu, gây thiệt hại <strong>~2 nghìn tỷ USD mỗi năm</strong>. Các hệ thống
            giám sát giao dịch thủ công không thể theo kịp tốc độ và khối lượng giao dịch của ví điện tử hiện đại.
          </p>
          <div style={{ marginTop: 24 }}>
            <IconBullet icon={AlertTriangle} text="Hàng triệu giao dịch mỗi ngày cần được sàng lọc" />
            <IconBullet icon={AlertTriangle} text="Các quy tắc cứng nhắc dễ bị lách luật" />
            <IconBullet icon={AlertTriangle} text="Cần giải thích được quyết định cho cơ quan quản lý" />
            <IconBullet icon={AlertTriangle} text="ML model cần kết hợp với domain knowledge" />
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
          <div className="slide-stat-callout">
            <div className="slide-stat-number">$2T</div>
            <div className="slide-stat-label">rửa tiền mỗi năm toàn cầu</div>
          </div>
          <div className="slide-stat-callout" style={{ marginTop: 16 }}>
            <div className="slide-stat-number">1%</div>
            <div className="slide-stat-label">tỷ lệ phát hiện hiện tại ước tính</div>
          </div>
        </div>
      </>,
      <>
        <div>
          <h2 className="slide-heading">The Problem</h2>
          <p className="slide-lead">
            Money laundering is a global issue, costing <strong>~$2 trillion annually</strong>. Manual
            transaction monitoring can't keep up with the speed and volume of modern e-wallet transactions.
          </p>
          <div style={{ marginTop: 24 }}>
            <IconBullet icon={AlertTriangle} text="Millions of daily transactions to screen" />
            <IconBullet icon={AlertTriangle} text="Rigid rules are easily circumvented" />
            <IconBullet icon={AlertTriangle} text="Regulators demand explainable decisions" />
            <IconBullet icon={AlertTriangle} text="ML models need domain knowledge integration" />
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
          <div className="slide-stat-callout">
            <div className="slide-stat-number">$2T</div>
            <div className="slide-stat-label">global money laundering per year</div>
          </div>
          <div className="slide-stat-callout" style={{ marginTop: 16 }}>
            <div className="slide-stat-number">~1%</div>
            <div className="slide-stat-label">estimated current detection rate</div>
          </div>
        </div>
      </>,
    ),
  },

  /* 3 — What is AnomalyX? */
  {
    id: "what-is",
    layout: "content",
    content: bilingual(
      <>
        <h2 className="slide-heading">AnomalyX là gì?</h2>
        <p className="slide-lead" style={{ maxWidth: 700, margin: "0 auto" }}>
          Hệ thống <strong>hybrid</strong> kết hợp rule engine truyền thống, machine learning, và LLM để phát
          hiện và giải thích giao dịch đáng ngờ trong thời gian thực.
        </p>
        <div className="slide-feature-grid">
          <div className="slide-feature-card">
            <Shield size={28} style={{ color: "var(--accent-primary)" }} />
            <strong>Rule Engine</strong>
            <span>Phát hiện 8+ AML typology qua YAML rules</span>
          </div>
          <div className="slide-feature-card">
            <BrainCircuit size={28} style={{ color: "var(--accent-secondary)" }} />
            <strong>ML Predictor</strong>
            <span>XGBoost prototype trên dữ liệu mô phỏng PaySim</span>
          </div>
          <div className="slide-feature-card">
            <FileText size={28} style={{ color: "var(--state-success)" }} />
            <strong>LLM Explainer</strong>
            <span>Giải thích bằng ngôn ngữ tự nhiên, dữ liệu được masked</span>
          </div>
          <div className="slide-feature-card">
            <BarChart3 size={28} style={{ color: "var(--state-info)" }} />
            <strong>Observability</strong>
            <span>Prometheus metrics, health checks, audit logs</span>
          </div>
        </div>
      </>,
      <>
        <h2 className="slide-heading">What is AnomalyX?</h2>
        <p className="slide-lead" style={{ maxWidth: 700, margin: "0 auto" }}>
          A <strong>hybrid</strong> system combining a traditional rule engine, machine learning, and LLM to
          detect and explain suspicious transactions in real time.
        </p>
        <div className="slide-feature-grid">
          <div className="slide-feature-card">
            <Shield size={28} style={{ color: "var(--accent-primary)" }} />
            <strong>Rule Engine</strong>
            <span>Detects 8+ AML typologies via YAML rules</span>
          </div>
          <div className="slide-feature-card">
            <BrainCircuit size={28} style={{ color: "var(--accent-secondary)" }} />
            <strong>ML Predictor</strong>
            <span>XGBoost prototype trained on PaySim synthetic data</span>
          </div>
          <div className="slide-feature-card">
            <FileText size={28} style={{ color: "var(--state-success)" }} />
            <strong>LLM Explainer</strong>
            <span>Natural-language explanations with masked data</span>
          </div>
          <div className="slide-feature-card">
            <BarChart3 size={28} style={{ color: "var(--state-info)" }} />
            <strong>Observability</strong>
            <span>Prometheus metrics, health checks, audit logs</span>
          </div>
        </div>
      </>,
    ),
  },

  /* 4 — Why Hybrid Architecture */
  {
    id: "why-hybrid",
    layout: "two-column",
    content: bilingual(
      <>
        <div>
          <h2 className="slide-heading">Tại sao Hybrid?</h2>
          <p className="slide-lead">
            Mỗi phương pháp riêng lẻ đều có điểm yếu. Kết hợp cả ba tạo ra hệ thống <strong>chính xác, linh hoạt, và giải thích được</strong>.
          </p>
          <div style={{ marginTop: 16 }}>
            <IconBullet icon={Shield} text="Rule Engine: phát hiện pattern đã biết với precision cao, nhưng không bắt được pattern mới" />
            <IconBullet icon={BrainCircuit} text="ML Model: phát hiện anomaly chưa biết, nhưng thiếu explainability và có false positive" />
            <IconBullet icon={FileText} text="LLM: giải thích tự nhiên cho compliance, nhưng cần context grounded từ rules + ML" />
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", gap: 16 }}>
          <div className="slide-info-card">
            <strong>🎯 Precision</strong>
            <span>Rule engine bắt pattern đã biết, ML model bắt pattern mới → kết hợp giảm false negative</span>
          </div>
          <div className="slide-info-card">
            <strong>🔄 Flexibility</strong>
            <span>Hot-reload rules không cần retrain ML. ML tự thích nghi với pattern mới không cần code thêm rule</span>
          </div>
          <div className="slide-info-card">
            <strong>📋 Explainability</strong>
            <span>Rule hits + SHAP features → LLM grounded explanation → compliance officer hiểu được lý do</span>
          </div>
        </div>
      </>,
      <>
        <div>
          <h2 className="slide-heading">Why Hybrid?</h2>
          <p className="slide-lead">
            Each method alone has weaknesses. Combining all three creates a system that is <strong>accurate, flexible, and explainable</strong>.
          </p>
          <div style={{ marginTop: 16 }}>
            <IconBullet icon={Shield} text="Rule Engine: catches known patterns with high precision, but misses novel attacks" />
            <IconBullet icon={BrainCircuit} text="ML Model: detects unknown anomalies, but lacks explainability and has false positives" />
            <IconBullet icon={FileText} text="LLM: natural explanations for compliance, but needs grounded context from rules + ML" />
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", gap: 16 }}>
          <div className="slide-info-card">
            <strong>🎯 Precision</strong>
            <span>Rule engine catches known patterns, ML catches novel ones → combined reduces false negatives</span>
          </div>
          <div className="slide-info-card">
            <strong>🔄 Flexibility</strong>
            <span>Hot-reload rules without retraining ML. ML adapts to new patterns without coding new rules</span>
          </div>
          <div className="slide-info-card">
            <strong>📋 Explainability</strong>
            <span>Rule hits + SHAP features → LLM grounded explanation → compliance officers understand the why</span>
          </div>
        </div>
      </>,
    ),
  },

  /* 5 — System Architecture (was 4) */
  {
    id: "architecture",
    layout: "demo",
    demoComponent: ArchitectureDiagram as React.FC<{ language: import("../types").Language; token: string }>,
    content: bilingual(
      <h2 className="slide-heading">Kiến trúc Hệ thống</h2>,
      <h2 className="slide-heading">System Architecture</h2>,
    ),
  },

  /* 5 — Prediction Pipeline */
  {
    id: "pipeline",
    layout: "content",
    content: bilingual(
      <>
        <h2 className="slide-heading">Pipeline Dự đoán</h2>
        <div className="slide-pipeline-flow">
          {[
            { step: "1", label: "Auth", desc: "Bearer token" },
            { step: "2", label: "Idempotency", desc: "Chống trùng lặp" },
            { step: "3", label: "Rules", desc: "YAML DSL" },
            { step: "4", label: "ML", desc: "XGBoost" },
            { step: "5", label: "Decision", desc: "Kết hợp" },
            { step: "6", label: "Alert", desc: "Cảnh báo" },
          ].map(({ step, label, desc }) => (
            <div key={step} className="slide-pipeline-step">
              <div className="slide-pipeline-num">{step}</div>
              <strong>{label}</strong>
              <span>{desc}</span>
            </div>
          ))}
        </div>
        <p className="slide-note" style={{ marginTop: 20 }}>
          Mỗi bước xử lý trong &lt;500ms. LLM chạy bất đồng bộ, không block response.
        </p>
      </>,
      <>
        <h2 className="slide-heading">Prediction Pipeline</h2>
        <div className="slide-pipeline-flow">
          {[
            { step: "1", label: "Auth", desc: "Bearer token" },
            { step: "2", label: "Idempotency", desc: "Dedup" },
            { step: "3", label: "Rules", desc: "YAML DSL" },
            { step: "4", label: "ML", desc: "XGBoost" },
            { step: "5", label: "Decision", desc: "Reconcile" },
            { step: "6", label: "Alert", desc: "Flag" },
          ].map(({ step, label, desc }) => (
            <div key={step} className="slide-pipeline-step">
              <div className="slide-pipeline-num">{step}</div>
              <strong>{label}</strong>
              <span>{desc}</span>
            </div>
          ))}
        </div>
        <p className="slide-note" style={{ marginTop: 20 }}>
          Each step processes in &lt;500ms. LLM runs async, never blocks the response.
        </p>
      </>,
    ),
  },

  /* 7 — Repository Structure */
  {
    id: "repo-structure",
    layout: "content",
    content: bilingual(
      <>
        <h2 className="slide-heading">Cấu trúc Dự án</h2>
        <div className="slide-repo-grid">
          <div className="slide-repo-col">
            <div className="slide-repo-item"><FolderTree size={14} /><strong>backend/</strong><span>FastAPI service</span></div>
            <div className="slide-repo-sub">├ app/api/v1/routes/ — endpoints</div>
            <div className="slide-repo-sub">├ app/services/ — business logic</div>
            <div className="slide-repo-sub">├ app/core/ — config, decision, errors</div>
            <div className="slide-repo-sub">├ app/ml/ — predictors (mock + XGBoost)</div>
            <div className="slide-repo-sub">├ app/rules/ — YAML rule engine</div>
            <div className="slide-repo-sub">├ app/llm/ — explainer + data masking</div>
            <div className="slide-repo-sub">├ app/repositories/ — persistence adapters</div>
            <div className="slide-repo-sub">├ db/schema.sql — PostgreSQL schema</div>
            <div className="slide-repo-sub">└ tests/ — pytest suite</div>
          </div>
          <div className="slide-repo-col">
            <div className="slide-repo-item"><FolderTree size={14} /><strong>frontend/</strong><span>React + Vite</span></div>
            <div className="slide-repo-sub">├ src/features/ — business modules</div>
            <div className="slide-repo-sub">├ src/shared/ — API client, UI, types</div>
            <div className="slide-repo-sub">└ src/styles/ — CSS + Tailwind</div>
            <div className="slide-repo-item" style={{ marginTop: 12 }}><FolderTree size={14} /><strong>ml/</strong><span>Training pipeline</span></div>
            <div className="slide-repo-sub">├ notebooks/ — EDA + experiments</div>
            <div className="slide-repo-sub">├ models/artifacts/ — serialized models</div>
            <div className="slide-repo-sub">└ Makefile — reproducible pipeline</div>
            <div className="slide-repo-item" style={{ marginTop: 12 }}><FolderTree size={14} /><strong>configs/</strong><span>rules.yaml</span></div>
            <div className="slide-repo-item"><FolderTree size={14} /><strong>docker-compose.yml</strong><span>Full stack</span></div>
          </div>
        </div>
      </>,
      <>
        <h2 className="slide-heading">Repository Structure</h2>
        <div className="slide-repo-grid">
          <div className="slide-repo-col">
            <div className="slide-repo-item"><FolderTree size={14} /><strong>backend/</strong><span>FastAPI service</span></div>
            <div className="slide-repo-sub">├ app/api/v1/routes/ — endpoints</div>
            <div className="slide-repo-sub">├ app/services/ — business logic</div>
            <div className="slide-repo-sub">├ app/core/ — config, decision, errors</div>
            <div className="slide-repo-sub">├ app/ml/ — predictors (mock + XGBoost)</div>
            <div className="slide-repo-sub">├ app/rules/ — YAML rule engine</div>
            <div className="slide-repo-sub">├ app/llm/ — explainer + data masking</div>
            <div className="slide-repo-sub">├ app/repositories/ — persistence adapters</div>
            <div className="slide-repo-sub">├ db/schema.sql — PostgreSQL schema</div>
            <div className="slide-repo-sub">└ tests/ — pytest suite</div>
          </div>
          <div className="slide-repo-col">
            <div className="slide-repo-item"><FolderTree size={14} /><strong>frontend/</strong><span>React + Vite</span></div>
            <div className="slide-repo-sub">├ src/features/ — business modules</div>
            <div className="slide-repo-sub">├ src/shared/ — API client, UI, types</div>
            <div className="slide-repo-sub">└ src/styles/ — CSS + Tailwind</div>
            <div className="slide-repo-item" style={{ marginTop: 12 }}><FolderTree size={14} /><strong>ml/</strong><span>Training pipeline</span></div>
            <div className="slide-repo-sub">├ notebooks/ — EDA + experiments</div>
            <div className="slide-repo-sub">├ models/artifacts/ — serialized models</div>
            <div className="slide-repo-sub">└ Makefile — reproducible pipeline</div>
            <div className="slide-repo-item" style={{ marginTop: 12 }}><FolderTree size={14} /><strong>configs/</strong><span>rules.yaml</span></div>
            <div className="slide-repo-item"><FolderTree size={14} /><strong>docker-compose.yml</strong><span>Full stack</span></div>
          </div>
        </div>
      </>,
    ),
  },

  /* 8 — Rule Engine (was 6) */
  {
    id: "rules",
    layout: "demo",
    demoComponent: RulesDemo as React.FC<{ language: import("../types").Language; token: string }>,
    content: bilingual(
      <>
        <h2 className="slide-heading">Rule Engine</h2>
        <p className="slide-note">
          Các rule được định nghĩa bằng YAML, đánh giá qua sandboxed AST. Hỗ trợ hot-reload không downtime.
          Phát hiện: structuring, smurfing, rapid movement, layering, threshold avoidance, velocity anomaly.
        </p>
      </>,
      <>
        <h2 className="slide-heading">Rule Engine</h2>
        <p className="slide-note">
          Rules defined in YAML, evaluated through a sandboxed AST. Supports hot-reload with zero downtime.
          Detects: structuring, smurfing, rapid movement, layering, threshold avoidance, velocity anomaly.
        </p>
      </>,
    ),
  },

  /* 7 — ML Prediction */
  {
    id: "ml",
    layout: "two-column",
    content: bilingual(
      <>
        <div>
          <h2 className="slide-heading">ML Prediction</h2>
          <p className="slide-lead">
            <strong>XGBoost</strong> model huấn luyện trên <strong>PaySim</strong> dataset (~6M giao dịch tổng
            hợp).
          </p>
          <div style={{ marginTop: 20 }}>
            <IconBullet icon={CheckCircle2} text="26 features: transaction, velocity, counterparty, behavioural, sequence, structuring" />
            <IconBullet icon={CheckCircle2} text="SHAP TreeExplainer — top-5 feature contributions" />
            <IconBullet icon={CheckCircle2} text="Calibrated probabilities (Platt scaling) → risk_score ∈ [0,1]" />
            <IconBullet icon={Target} text="Target: Precision ≥ 0.70 | Recall ≥ 0.60 | PR-AUC ≥ 0.50" />
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", gap: 12 }}>
          <div className="slide-stat-callout slide-stat-callout--success">
            <div className="slide-stat-number">PR-AUC</div>
            <div className="slide-stat-label">primary metric for imbalanced data</div>
          </div>
          <div className="slide-stat-callout" style={{ marginTop: 16 }}>
            <div className="slide-stat-number">26</div>
            <div className="slide-stat-label">features</div>
          </div>
        </div>
      </>,
      <>
        <div>
          <h2 className="slide-heading">ML Prediction</h2>
          <p className="slide-lead">
            <strong>XGBoost</strong> model trained on the <strong>PaySim</strong> dataset (~6M synthetic
            transactions).
          </p>
          <div style={{ marginTop: 20 }}>
            <IconBullet icon={CheckCircle2} text="26 features: transaction, velocity, counterparty, behavioural, sequence, structuring" />
            <IconBullet icon={CheckCircle2} text="SHAP TreeExplainer — top-5 feature contributions" />
            <IconBullet icon={CheckCircle2} text="Calibrated probabilities (Platt scaling) → risk_score ∈ [0,1]" />
            <IconBullet icon={Target} text="Target: Precision ≥ 0.70 | Recall ≥ 0.60 | PR-AUC ≥ 0.50" />
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", gap: 12 }}>
          <div className="slide-stat-callout slide-stat-callout--success">
            <div className="slide-stat-number">PR-AUC</div>
            <div className="slide-stat-label">primary metric for imbalanced data</div>
          </div>
          <div className="slide-stat-callout" style={{ marginTop: 16 }}>
            <div className="slide-stat-number">26</div>
            <div className="slide-stat-label">features</div>
          </div>
        </div>
      </>,
    ),
  },

  /* 8 — Live Prediction Demo */
  {
    id: "predict-demo",
    layout: "demo",
    demoComponent: PredictDemo as React.FC<{ language: import("../types").Language; token: string }>,
    content: bilingual(
      <>
        <h2 className="slide-heading">Demo: Dự đoán Trực tiếp</h2>
        <p className="slide-note">Gửi một giao dịch thật đến API và xem kết quả ngay trong slide.</p>
      </>,
      <>
        <h2 className="slide-heading">Demo: Live Prediction</h2>
        <p className="slide-note">Submit a real transaction to the API and see the result live in this slide.</p>
      </>,
    ),
  },

  /* 9 — Decision Engine */
  {
    id: "decision",
    layout: "content",
    content: bilingual(
      <>
        <h2 className="slide-heading">Decision Engine</h2>
        <p className="slide-lead" style={{ maxWidth: 650, margin: "0 auto 24px" }}>
          Kết hợp <strong>rule severity</strong> và <strong>ML risk score</strong> để ra quyết định cuối cùng.
        </p>
        <table className="slide-decision-table">
          <thead>
            <tr>
              <th>Rule Severity</th>
              <th>ML Score</th>
              <th>Kết quả</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><span className="badge badge--critical">CRITICAL</span></td>
              <td>Bất kỳ</td>
              <td><strong>CRITICAL</strong> — luôn flag</td>
            </tr>
            <tr>
              <td><span className="badge badge--high">HIGH</span></td>
              <td>Bất kỳ</td>
              <td><strong>HIGH</strong> — luôn flag</td>
            </tr>
            <tr>
              <td>Không có</td>
              <td>≥ 0.70</td>
              <td><strong>HIGH</strong> — flag</td>
            </tr>
            <tr>
              <td>Không có</td>
              <td>0.40 – 0.70</td>
              <td><strong>MEDIUM</strong> — log only</td>
            </tr>
            <tr>
              <td>Không có</td>
              <td>&lt; 0.40</td>
              <td><strong>LOW</strong></td>
            </tr>
          </tbody>
        </table>
      </>,
      <>
        <h2 className="slide-heading">Decision Engine</h2>
        <p className="slide-lead" style={{ maxWidth: 650, margin: "0 auto 24px" }}>
          Reconciles <strong>rule severity</strong> and <strong>ML risk score</strong> into the final decision.
        </p>
        <table className="slide-decision-table">
          <thead>
            <tr>
              <th>Rule Severity</th>
              <th>ML Score</th>
              <th>Result</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><span className="badge badge--critical">CRITICAL</span></td>
              <td>Any</td>
              <td><strong>CRITICAL</strong> — always flagged</td>
            </tr>
            <tr>
              <td><span className="badge badge--high">HIGH</span></td>
              <td>Any</td>
              <td><strong>HIGH</strong> — always flagged</td>
            </tr>
            <tr>
              <td>None</td>
              <td>≥ 0.70</td>
              <td><strong>HIGH</strong> — flagged</td>
            </tr>
            <tr>
              <td>None</td>
              <td>0.40 – 0.70</td>
              <td><strong>MEDIUM</strong> — log only</td>
            </tr>
            <tr>
              <td>None</td>
              <td>&lt; 0.40</td>
              <td><strong>LOW</strong></td>
            </tr>
          </tbody>
        </table>
      </>,
    ),
  },

  /* 10 — Alert System */
  {
    id: "alerts",
    layout: "demo",
    demoComponent: AlertsDemo as React.FC<{ language: import("../types").Language; token: string }>,
    content: bilingual(
      <>
        <h2 className="slide-heading">Hệ thống Cảnh báo</h2>
        <p className="slide-note">Alert được tạo tự động khi giao dịch bị flag. Hỗ trợ review workflow: NEW → ESCALATED/DISMISSED.</p>
      </>,
      <>
        <h2 className="slide-heading">Alert System</h2>
        <p className="slide-note">Alerts are created automatically for flagged transactions. Supports review workflow: NEW → ESCALATED/DISMISSED.</p>
      </>,
    ),
  },

  /* 11 — LLM Explanation */
  {
    id: "llm",
    layout: "two-column",
    content: bilingual(
      <>
        <div>
          <h2 className="slide-heading">LLM Explanation</h2>
          <p className="slide-lead">Giải thích bằng ngôn ngữ tự nhiên, bất đồng bộ, an toàn về dữ liệu.</p>
          <div style={{ marginTop: 20 }}>
            <IconBullet icon={Shield} text="Dữ liệu được masked trước khi gửi đến LLM" />
            <IconBullet icon={Workflow} text="Fallback về template nếu LLM lỗi" />
            <IconBullet icon={Server} text="Chạy trong FastAPI BackgroundTasks" />
            <IconBullet icon={CheckCircle2} text="Hỗ trợ song ngữ VI + EN" />
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", gap: 12 }}>
          <div className="slide-info-card">
            <strong>1. Nhận alert</strong>
            <span>Transaction bị flag → enqueue background task</span>
          </div>
          <ArrowRight size={20} style={{ alignSelf: "center", opacity: 0.5 }} />
          <div className="slide-info-card">
            <strong>2. Mask & Prompt</strong>
            <span>SecureDataWrapper loại bỏ PII, chỉ gửi feature context</span>
          </div>
          <ArrowRight size={20} style={{ alignSelf: "center", opacity: 0.5 }} />
          <div className="slide-info-card">
            <strong>3. Validate & Store</strong>
            <span>Output được kiểm tra trước khi lưu — nếu fail → template fallback</span>
          </div>
        </div>
      </>,
      <>
        <div>
          <h2 className="slide-heading">LLM Explanation</h2>
          <p className="slide-lead">Natural-language explanations, async, data-safe.</p>
          <div style={{ marginTop: 20 }}>
            <IconBullet icon={Shield} text="Data masked before sending to LLM" />
            <IconBullet icon={Workflow} text="Template fallback on LLM failure" />
            <IconBullet icon={Server} text="Runs in FastAPI BackgroundTasks" />
            <IconBullet icon={CheckCircle2} text="Bilingual VI + EN support" />
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", gap: 12 }}>
          <div className="slide-info-card">
            <strong>1. Alert received</strong>
            <span>Flagged transaction → enqueue background task</span>
          </div>
          <ArrowRight size={20} style={{ alignSelf: "center", opacity: 0.5 }} />
          <div className="slide-info-card">
            <strong>2. Mask & Prompt</strong>
            <span>SecureDataWrapper removes PII, sends feature context only</span>
          </div>
          <ArrowRight size={20} style={{ alignSelf: "center", opacity: 0.5 }} />
          <div className="slide-info-card">
            <strong>3. Validate & Store</strong>
            <span>Output validated before persistence — if fails → template fallback</span>
          </div>
        </div>
      </>,
    ),
  },

  /* 12 — Observability */
  {
    id: "observability",
    layout: "demo",
    demoComponent: HealthDemo as React.FC<{ language: import("../types").Language; token: string }>,
    content: bilingual(
      <>
        <h2 className="slide-heading">Observability</h2>
        <p className="slide-note">Health checks và Prometheus metrics endpoints công khai. Hiển thị trạng thái dịch vụ, model version, request volume, latency, và decision distribution.</p>
      </>,
      <>
        <h2 className="slide-heading">Observability</h2>
        <p className="slide-note">Public health checks and Prometheus metrics endpoints. Shows service status, model version, request volume, latency, and decision distribution.</p>
      </>,
    ),
  },

  /* 13 — Frontend & Design System */
  {
    id: "frontend",
    layout: "content",
    content: bilingual(
      <>
        <h2 className="slide-heading">Frontend &amp; Design System</h2>
        <div className="slide-feature-grid">
          <div className="slide-feature-card">
            <Layers size={28} style={{ color: "var(--accent-secondary)" }} />
            <strong>React 19 + Vite 7</strong>
            <span>TypeScript, HMR, tối ưu build</span>
          </div>
          <div className="slide-feature-card">
            <Cpu size={28} style={{ color: "var(--accent-primary)" }} />
            <strong>TanStack Query v5</strong>
            <span>Server state, cache, auto-refresh</span>
          </div>
          <div className="slide-feature-card">
            <Database size={28} style={{ color: "var(--state-info)" }} />
            <strong>Tailwind CSS v4</strong>
            <span>Dark/Light theme, CSS variables</span>
          </div>
          <div className="slide-feature-card">
            <Server size={28} style={{ color: "var(--state-success)" }} />
            <strong>Lucide Icons</strong>
            <span>Consistent icon system</span>
          </div>
        </div>
      </>,
      <>
        <h2 className="slide-heading">Frontend &amp; Design System</h2>
        <div className="slide-feature-grid">
          <div className="slide-feature-card">
            <Layers size={28} style={{ color: "var(--accent-secondary)" }} />
            <strong>React 19 + Vite 7</strong>
            <span>TypeScript, HMR, optimized builds</span>
          </div>
          <div className="slide-feature-card">
            <Cpu size={28} style={{ color: "var(--accent-primary)" }} />
            <strong>TanStack Query v5</strong>
            <span>Server state, cache, auto-refresh</span>
          </div>
          <div className="slide-feature-card">
            <Database size={28} style={{ color: "var(--state-info)" }} />
            <strong>Tailwind CSS v4</strong>
            <span>Dark/Light theme, CSS variables</span>
          </div>
          <div className="slide-feature-card">
            <Server size={28} style={{ color: "var(--state-success)" }} />
            <strong>Lucide Icons</strong>
            <span>Consistent icon system</span>
          </div>
        </div>
      </>,
    ),
  },

  /* 16 — Key Design Decisions */
  {
    id: "design-decisions",
    layout: "content",
    content: bilingual(
      <>
        <h2 className="slide-heading">Quyết định Thiết kế Chính</h2>
        <div className="slide-repo-grid">
          <div className="slide-repo-col">
            <div className="slide-repo-item"><Lightbulb size={14} /><strong>Tại sao XGBoost?</strong></div>
            <div className="slide-repo-sub">• Mạnh trên tabular data với heterogeneous features</div>
            <div className="slide-repo-sub">• Native SHAP support cho explainability</div>
            <div className="slide-repo-sub">• CPU-only inference, không cần GPU</div>
            <div className="slide-repo-sub">• PR-AUC làm metric chính (imbalanced data)</div>
            <div className="slide-repo-item" style={{ marginTop: 12 }}><Lightbulb size={14} /><strong>Tại sao FastAPI?</strong></div>
            <div className="slide-repo-sub">• Async native (BackgroundTasks cho LLM)</div>
            <div className="slide-repo-sub">• Pydantic validation → OpenAPI auto-generated</div>
            <div className="slide-repo-sub">• Dependency injection cho testability</div>
          </div>
          <div className="slide-repo-col">
            <div className="slide-repo-item"><Lightbulb size={14} /><strong>Tại sao Modular Monolith?</strong></div>
            <div className="slide-repo-sub">• Simpler deployment (single container)</div>
            <div className="slide-repo-sub">• Factory pattern cho env-switched backends</div>
            <div className="slide-repo-sub">• In-memory repos cho tests, Postgres cho prod</div>
            <div className="slide-repo-item" style={{ marginTop: 12 }}><Lightbulb size={14} /><strong>Data Privacy First</strong></div>
            <div className="slide-repo-sub">• Không lưu raw transaction payload</div>
            <div className="slide-repo-sub">• HMAC-SHA256 hashed identifiers</div>
            <div className="slide-repo-sub">• SecureDataWrapper mask PII trước LLM prompt</div>
          </div>
        </div>
      </>,
      <>
        <h2 className="slide-heading">Key Design Decisions</h2>
        <div className="slide-repo-grid">
          <div className="slide-repo-col">
            <div className="slide-repo-item"><Lightbulb size={14} /><strong>Why XGBoost?</strong></div>
            <div className="slide-repo-sub">• Strong on tabular data with heterogeneous features</div>
            <div className="slide-repo-sub">• Native SHAP support for explainability</div>
            <div className="slide-repo-sub">• CPU-only inference, no GPU required</div>
            <div className="slide-repo-sub">• PR-AUC as primary metric (imbalanced data)</div>
            <div className="slide-repo-item" style={{ marginTop: 12 }}><Lightbulb size={14} /><strong>Why FastAPI?</strong></div>
            <div className="slide-repo-sub">• Native async (BackgroundTasks for LLM)</div>
            <div className="slide-repo-sub">• Pydantic validation → auto-generated OpenAPI</div>
            <div className="slide-repo-sub">• Dependency injection for testability</div>
          </div>
          <div className="slide-repo-col">
            <div className="slide-repo-item"><Lightbulb size={14} /><strong>Why Modular Monolith?</strong></div>
            <div className="slide-repo-sub">• Simpler deployment (single container)</div>
            <div className="slide-repo-sub">• Factory pattern for env-switched backends</div>
            <div className="slide-repo-sub">• In-memory repos for tests, Postgres for prod</div>
            <div className="slide-repo-item" style={{ marginTop: 12 }}><Lightbulb size={14} /><strong>Data Privacy First</strong></div>
            <div className="slide-repo-sub">• No raw transaction payload storage</div>
            <div className="slide-repo-sub">• HMAC-SHA256 hashed identifiers</div>
            <div className="slide-repo-sub">• SecureDataWrapper masks PII before LLM prompt</div>
          </div>
        </div>
      </>,
    ),
  },

  /* 17 — Infrastructure & Roadmap (was 14) */
  {
    id: "roadmap",
    layout: "two-column",
    content: bilingual(
      <>
        <div>
          <h2 className="slide-heading">Infrastructure</h2>
          <div style={{ marginTop: 20 }}>
            <IconBullet icon={Server} text="Docker Compose: API + PostgreSQL + Redis" />
            <IconBullet icon={Database} text="PostgreSQL 16 cho alerts, review_labels, prediction_logs" />
            <IconBullet icon={Workflow} text="Redis 7 cho idempotency store" />
            <IconBullet icon={CheckCircle2} text="Git LFS cho ML artifacts" />
          </div>
        </div>
        <div>
          <h2 className="slide-heading">Roadmap</h2>
          <div style={{ marginTop: 20 }}>
            <IconBullet icon={ArrowRight} text="Redis rolling aggregates (velocity features)" />
            <IconBullet icon={ArrowRight} text="Real drift detection + explanation cache" />
            <IconBullet icon={ArrowRight} text="Unit tests cho XGBPredictor" />
            <IconBullet icon={ArrowRight} text="Production deployment hardening" />
          </div>
        </div>
      </>,
      <>
        <div>
          <h2 className="slide-heading">Infrastructure</h2>
          <div style={{ marginTop: 20 }}>
            <IconBullet icon={Server} text="Docker Compose: API + PostgreSQL + Redis" />
            <IconBullet icon={Database} text="PostgreSQL 16 for alerts, review_labels, prediction_logs" />
            <IconBullet icon={Workflow} text="Redis 7 for idempotency store" />
            <IconBullet icon={CheckCircle2} text="Git LFS for ML artifacts" />
          </div>
        </div>
        <div>
          <h2 className="slide-heading">Roadmap</h2>
          <div style={{ marginTop: 20 }}>
            <IconBullet icon={ArrowRight} text="Redis rolling aggregates (velocity features)" />
            <IconBullet icon={ArrowRight} text="Real drift detection + explanation cache" />
            <IconBullet icon={ArrowRight} text="XGBPredictor unit tests" />
            <IconBullet icon={ArrowRight} text="Production deployment hardening" />
          </div>
        </div>
      </>,
    ),
  },

  /* 15 — Thank You / Q&A */
  {
    id: "ending",
    layout: "ending",
    background: "accent",
    content: bilingual(
      <>
        <h1 className="slide-ending-title">Cảm ơn!</h1>
        <p className="slide-ending-sub">Câu hỏi &amp; Thảo luận</p>
        <div className="slide-tag-row" style={{ marginTop: 32 }}>
          <Tag>github.com/PaimonZero/AnomalyX</Tag>
        </div>
      </>,
      <>
        <h1 className="slide-ending-title">Thank You!</h1>
        <p className="slide-ending-sub">Questions &amp; Discussion</p>
        <div className="slide-tag-row" style={{ marginTop: 32 }}>
          <Tag>github.com/PaimonZero/AnomalyX</Tag>
        </div>
      </>,
    ),
  },
];

const presentationOrder = [
  "title",
  "problem",
  "what-is",
  "why-hybrid",
  "architecture",
  "rules",
  "ml",
  "decision",
  "llm",
  "pipeline",
  "repo-structure",
  "ending",
];

export const slides: Slide[] = presentationOrder.map((id) => {
  const slide = slideDefinitions.find((item) => item.id === id);
  if (!slide) {
    throw new Error(`Missing presentation slide: ${id}`);
  }
  return slide;
});
