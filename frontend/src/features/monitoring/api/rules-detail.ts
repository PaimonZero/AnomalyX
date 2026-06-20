import type { RuleEngineDetails } from "@/features/monitoring/api/rules-detail-format";
import { apiRequest } from "@/shared/api/client";

export function getRuleEngineDetails(token: string) {
  return apiRequest<RuleEngineDetails>("/rules", { token });
}
