import { api } from "@/lib/axios";

import type { MenuItem, MenuValues } from "./types";

export function getMenuItems(is_available?: boolean) {
  return api.get<MenuItem[]>("/menu/", {
    params: is_available !== undefined ? { is_available } : undefined,
  });
}

export function getMenuItem(id: string) {
  return api.get<MenuItem>(`/menu/${id}`);
}

export function createMenu(data: MenuValues) {
  return api.post<MenuItem>("/menu/", {
    ...data,
    description: data.description || null,
  });
}

export function updateMenu(id: string, data: MenuValues) {
  return api.patch<MenuItem>(`/menu/${id}`, {
    ...data,
    description: data.description || null,
  });
}

export function updateMenuAvailability(id: string, isAvailable: boolean) {
  return api.patch<MenuItem>(`/menu/${id}/availability`, undefined, {
    params: { is_available: isAvailable },
  });
}

export function deleteMenu(id: string) {
  return api.delete<null>(`/menu/${id}`);
}
