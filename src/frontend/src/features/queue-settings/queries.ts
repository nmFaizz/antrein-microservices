import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type {
  QueueSettingsCreatePayload,
  QueueSettingsUpdatePayload,
} from "@/features/queue/types";

import { createSettings, getSettings, updateSettings } from "./api";

export const settingsKeys = {
  all: ["queue-settings"] as const,
};

/**
 * Fetch the active queue settings. Returns an error when none are configured
 * (backend 409) — `retry: false` surfaces that immediately so the page can
 * show the "create settings first" flow.
 */
export function useSettings() {
  return useQuery({
    queryKey: settingsKeys.all,
    queryFn: getSettings,
    retry: false,
  });
}

export function useCreateSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: QueueSettingsCreatePayload) =>
      createSettings(payload),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: settingsKeys.all }),
  });
}

export function useUpdateSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: string;
      payload: QueueSettingsUpdatePayload;
    }) => updateSettings(id, payload),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: settingsKeys.all }),
  });
}
