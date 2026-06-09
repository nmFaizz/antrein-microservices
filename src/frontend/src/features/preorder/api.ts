import { api } from "@/lib/axios";

import type { Preorder } from "./types";

export interface PreorderCreatePayload {
  notes?: string | null;
  items: { menu_item_id: string; quantity: number }[];
}

export interface PreorderUpdatePayload {
  status?: "pending" | "confirmed" | "cancelled";
}

export function getMyPreorders() {
  return api.get<Preorder[]>("/preorders/me");
}

export function getAllPreorders() {
  return api.get<Preorder[]>("/preorders/");
}

export function createPreorder(data: PreorderCreatePayload) {
  return api.post<Preorder>("/preorders/", data);
}

export function updatePreorder(id: string, data: PreorderUpdatePayload) {
  return api.patch<Preorder>(`/preorders/${id}`, data);
}

export function cancelPreorder(id: string) {
  return api.patch<Preorder>(`/preorders/${id}/cancel`);
}
