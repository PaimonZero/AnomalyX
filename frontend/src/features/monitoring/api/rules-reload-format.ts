export interface ReloadRulesResponse {
  status: "reloaded";
  active_rules: number;
  version: string;
}

export function formatReloadRulesSuccess(response: ReloadRulesResponse) {
  return `Backend rules reloaded successfully. ${response.active_rules} active rules · version ${response.version}.`;
}
