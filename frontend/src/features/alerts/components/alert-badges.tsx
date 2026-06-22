import { Badge } from "@/shared/ui/badge";
import type { AlertStatus, RiskLevel } from "@/shared/types/api";
import type { ExplanationSource } from "@/features/alerts/types";

export function RiskBadge({ level }: { level: RiskLevel }) {
  const tone = level === "CRITICAL" ? "critical" : level === "HIGH" ? "high" : level === "MEDIUM" ? "warning" : "success";
  return <Badge tone={tone}>{level}</Badge>;
}

export function StatusBadge({ status }: { status: AlertStatus }) {
  const tone = status === "ESCALATED" ? "critical" : status === "DISMISSED" ? "neutral" : "info";
  return <Badge tone={tone}>{status}</Badge>;
}

export function SourceBadge({ source }: { source: ExplanationSource }) {
  if (source === "pending") return <Badge tone="warning">PENDING</Badge>;
  return <Badge tone={source === "llm" ? "accent" : "neutral"}>{source.toUpperCase()}</Badge>;
}

