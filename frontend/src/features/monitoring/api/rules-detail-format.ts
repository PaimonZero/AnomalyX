export interface RuleConfig {
  id: string;
  name?: string;
  typology?: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  enabled: boolean;
  condition?: string;
  action_hint?: string | null;
}

export interface RuleEngineDetails {
  version: number | string;
  rules: RuleConfig[];
}

export function summarizeRuleEngine(details: RuleEngineDetails) {
  const enabledCount = details.rules.filter((rule) => rule.enabled).length;
  return `${enabledCount}/${details.rules.length} enabled · version ${details.version}`;
}

export function formatRuleTypology(rule: RuleConfig) {
  return (rule.typology || rule.name || "No typology").replaceAll("_", " ");
}
