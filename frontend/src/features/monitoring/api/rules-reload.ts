import { apiRequest } from "@/shared/api/client";
import type { ReloadRulesResponse } from "@/features/monitoring/api/rules-reload-format";

export function reloadRules(token: string) {
  return apiRequest<ReloadRulesResponse>("/rules/reload", {
    method: "POST",
    token,
  });
}
