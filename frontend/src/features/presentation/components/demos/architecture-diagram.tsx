import { useEffect, useState } from "react";
import { AlertTriangle, ArrowRight, CheckCircle2, Cpu, Database, Server, Workflow } from "lucide-react";
import type { Language } from "../../types";

const LABELS: Record<string, { vi: string; en: string }> = {
  transaction: { vi: "Giao dịch", en: "Transaction" },
  auth: { vi: "Xác thực", en: "Auth" },
  idempotency: { vi: "Idempotency", en: "Idempotency" },
  rules: { vi: "Rule Engine", en: "Rule Engine" },
  ml: { vi: "ML Predictor", en: "ML Predictor" },
  decision: { vi: "Decision Engine", en: "Decision Engine" },
  alert: { vi: "Alert / Response", en: "Alert / Response" },
  postgres: { vi: "PostgreSQL", en: "PostgreSQL" },
  redis: { vi: "Redis", en: "Redis" },
  llm: { vi: "LLM (OpenAI)", en: "LLM (OpenAI)" },
};

const MAIN_IDS = ["transaction", "auth", "idempotency", "rules", "ml", "decision", "alert"];
const SUPPORT_IDS = ["postgres", "redis", "llm"];

export function ArchitectureDiagram({ language }: { language: Language; token: string }) {
  const [activeIdx, setActiveIdx] = useState(-1);

  useEffect(() => {
    let i = 0;
    const total = MAIN_IDS.length;
    const interval = setInterval(() => {
      setActiveIdx(i);
      i += 1;
      if (i > total) {
        clearInterval(interval);
        setTimeout(() => setActiveIdx(-1), 2500);
      }
    }, 500);
    return () => clearInterval(interval);
  }, []);

  const isActive = (id: string) => MAIN_IDS.indexOf(id) <= activeIdx;
  const supportActive = activeIdx >= MAIN_IDS.length;

  return (
    <div className="arch-diagram">
      {/* Main pipeline row */}
      <div className="arch-main-row">
        {MAIN_IDS.map((id, idx) => (
          <div key={id} className={`arch-node arch-node--main ${isActive(id) ? "arch-node--active" : ""}`}>
            <div className="arch-node-icon">
              {id === "transaction" && <Workflow size={24} />}
              {id === "auth" && <AlertTriangle size={24} />}
              {id === "idempotency" && <CheckCircle2 size={24} />}
              {(id === "rules" || id === "ml") && <Cpu size={24} />}
              {id === "decision" && <AlertTriangle size={24} />}
              {id === "alert" && <CheckCircle2 size={24} />}
            </div>
            <span className="arch-node-label">{LABELS[id][language]}</span>
            {idx < MAIN_IDS.length - 1 && (
              <ArrowRight
                size={18}
                className={`arch-arrow-icon ${activeIdx > idx ? "arch-arrow-icon--active" : ""}`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Divider */}
      <div className="arch-divider">
        <span>{language === "vi" ? "Dịch vụ hỗ trợ" : "Supporting Services"}</span>
      </div>

      {/* Support row */}
      <div className="arch-support-row">
        {SUPPORT_IDS.map((id) => (
          <div key={id} className={`arch-node arch-node--support ${supportActive ? "arch-node--active" : ""}`}>
            <div className="arch-node-icon">
              {(id === "postgres" || id === "redis") && <Database size={20} />}
              {id === "llm" && <Server size={20} />}
            </div>
            <span className="arch-node-label">{LABELS[id][language]}</span>
          </div>
        ))}
      </div>

      <p className="arch-caption">
        {language === "vi"
          ? "Pipeline xử lý chính bên trên. PostgreSQL, Redis, và LLM là các dịch vụ hỗ trợ."
          : "Main processing pipeline above. PostgreSQL, Redis, and LLM are supporting services."}
      </p>
    </div>
  );
}
