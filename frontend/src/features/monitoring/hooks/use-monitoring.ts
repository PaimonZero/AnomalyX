import { useQuery } from "@tanstack/react-query";

import { getMonitoringHealth, getMonitoringMetrics } from "@/features/monitoring/api/monitoring-api";

export function useMonitoring(autoRefresh: boolean) {
  const refreshInterval = autoRefresh ? 30_000 : false;
  const health = useQuery({
    queryKey: ["monitoring", "health"],
    queryFn: getMonitoringHealth,
    refetchInterval: refreshInterval,
  });
  const metrics = useQuery({
    queryKey: ["monitoring", "metrics"],
    queryFn: getMonitoringMetrics,
    refetchInterval: refreshInterval,
  });

  return {
    health,
    metrics,
    refresh: async () => Promise.all([health.refetch(), metrics.refetch()]),
  };
}
