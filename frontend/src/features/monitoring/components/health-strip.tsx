import { Activity, BrainCircuit, Database, GitBranch, KeyRound } from "lucide-react";

import type { MonitoringHealth } from "@/features/monitoring/types";

interface HealthStripProps {
  health: MonitoringHealth;
  onOpenRuleDetails?: () => void;
}

export function HealthStrip({ health, onOpenRuleDetails }: HealthStripProps) {
  const items = [
    { label: "API service", up: health.status === "ok", detail: health.environment, icon: Activity },
    { label: "ML model", up: health.checks.model_configured, detail: health.model.version, icon: BrainCircuit },
    { label: "Rule engine", up: health.checks.rules_loaded, detail: "rules loaded", icon: GitBranch },
    { label: "Alert storage", up: health.checks.alert_repository_ready, detail: health.storage.alert_repository, icon: Database },
    { label: "Idempotency", up: health.checks.idempotency_configured, detail: health.storage.idempotency_store, icon: KeyRound },
  ];

  return (
    <section className="health-strip" aria-label="System health">
      {items.map(({ detail, icon: Icon, label, up }) => (
        <article key={label}>
          <Icon size={17} />
          <div>
            <span>{label}</span>
            <small>{detail}</small>
            {label === "Rule engine" && onOpenRuleDetails ? (
              <button className="health-detail-link" type="button" onClick={onOpenRuleDetails}>
                Detail
              </button>
            ) : null}
          </div>
          <strong className={up ? "health-up" : "health-down"}><i />{up ? "UP" : "DOWN"}</strong>
        </article>
      ))}
    </section>
  );
}
