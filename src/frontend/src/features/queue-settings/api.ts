import type {
  QueueSettings,
  QueueSettingsCreatePayload,
  QueueSettingsUpdatePayload,
} from "@/features/queue/types";
import { api } from "@/lib/axios";

export function getSettings() {
  return api.get<QueueSettings>("/queue-settings");
}

export function createSettings(payload: QueueSettingsCreatePayload) {
  return api.post<QueueSettings>("/queue-settings", payload);
}

export function updateSettings(
  id: string,
  payload: QueueSettingsUpdatePayload,
) {
  return api.patch<QueueSettings>(`/queue-settings/${id}`, payload);
}
