import { api } from "@/lib/axios";

import type { Queue } from "./types";

export function getQueues(params?: { queue_date?: string }) {
  return api.get<Queue[]>("/queues/", { params });
}

export function callNext(queue_date?: string) {
  return api.post<Queue>("/queues/call-next", { queue_date: queue_date ?? null });
}

export function serveQueue(id: string) {
  return api.post<Queue>(`/queues/${id}/serve`, {});
}

export function skipQueue(id: string, notes?: string) {
  return api.post<Queue>(`/queues/${id}/skip`, {
    trigger_type: "admin",
    notes: notes ?? null,
  });
}

export function requeueQueue(id: string) {
  return api.post<Queue>(`/queues/${id}/requeue`, {});
}

export function cancelQueue(id: string) {
  return api.post<Queue>(`/queues/${id}/cancel`, {});
}
