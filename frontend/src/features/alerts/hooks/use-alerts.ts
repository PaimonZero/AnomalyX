import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useAuthToken } from "@/app/providers/auth-token-context";
import { getAlert, listAlerts, updateAlertStatus } from "@/features/alerts/api/alerts-api";
import type { AlertFilters, UpdateAlertStatusInput } from "@/features/alerts/types";

const alertsKey = ["alerts"] as const;

export function useAlerts(filters: AlertFilters) {
  const { token } = useAuthToken();
  return useQuery({
    queryKey: [...alertsKey, filters, token],
    queryFn: () => listAlerts(filters, token),
  });
}

export function useAlertDetail(alertId: string | null) {
  const { token } = useAuthToken();
  return useQuery({
    queryKey: [...alertsKey, "detail", alertId, token],
    queryFn: () => getAlert(alertId!, token),
    enabled: Boolean(alertId),
  });
}

export function useUpdateAlertStatus() {
  const queryClient = useQueryClient();
  const { token } = useAuthToken();

  return useMutation({
    mutationFn: (input: UpdateAlertStatusInput) => updateAlertStatus(input, token),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: alertsKey });
    },
  });
}
