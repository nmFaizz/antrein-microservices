import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createMenu,
  deleteMenu,
  getMenuItem,
  getMenuItems,
  updateMenu,
  updateMenuAvailability,
} from "./api";
import type { MenuValues } from "./types";

export const menuKeys = {
  all: ["menu"] as const,
  list: () => [...menuKeys.all, "list"] as const,
  detail: (id: string) => [...menuKeys.all, "detail", id] as const,
};

export function useMenuItems() {
  return useQuery({
    queryKey: menuKeys.list(),
    queryFn: () => getMenuItems(),
  });
}

export function useMenuItem(id: string) {
  return useQuery({
    queryKey: menuKeys.detail(id),
    queryFn: () => getMenuItem(id),
    enabled: !!id,
  });
}

export function useCreateMenu() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: MenuValues) => createMenu(data),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: menuKeys.list() }),
  });
}

export function useUpdateMenu() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: MenuValues }) =>
      updateMenu(id, data),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: menuKeys.list() }),
  });
}

export function useUpdateMenuAvailability() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, isAvailable }: { id: string; isAvailable: boolean }) =>
      updateMenuAvailability(id, isAvailable),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: menuKeys.list() }),
  });
}

export function useDeleteMenu() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteMenu(id),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: menuKeys.list() }),
  });
}
