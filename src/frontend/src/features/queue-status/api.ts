import type {
  QueueStatus,
  QueueStatusCreatePayload,
  QueueStatusUpdatePayload,
} from "@/features/queue/types";
import { api } from "@/lib/axios";

export function getStatuses() {
  return api.get<QueueStatus[]>("/queue-statuses");
}

export function createStatus(payload: QueueStatusCreatePayload) {
  return api.post<QueueStatus>("/queue-statuses", payload);
}

export function updateStatus(id: string, payload: QueueStatusUpdatePayload) {
  return api.patch<QueueStatus>(`/queue-statuses/${id}`, payload);
}

export function deleteStatus(id: string) {
  return api.delete<null>(`/queue-statuses/${id}`);
}
