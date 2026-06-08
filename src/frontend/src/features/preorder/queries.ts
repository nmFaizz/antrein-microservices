import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  cancelPreorder,
  createPreorder,
  getAllPreorders,
  getMyPreorders,
  updatePreorder,
  type PreorderCreatePayload,
  type PreorderUpdatePayload,
} from "./api";

export const preorderKeys = {
  all: ["preorders"] as const,
  mine: () => [...preorderKeys.all, "me"] as const,
  admin: () => [...preorderKeys.all, "admin"] as const,
};

export function useMyPreorders() {
  return useQuery({
    queryKey: preorderKeys.mine(),
    queryFn: getMyPreorders,
  });
}

export function useAllPreorders() {
  return useQuery({
    queryKey: preorderKeys.admin(),
    queryFn: getAllPreorders,
  });
}

export function useCreatePreorder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: PreorderCreatePayload) => createPreorder(data),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: preorderKeys.mine() }),
  });
}

export function useUpdatePreorder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: PreorderUpdatePayload }) =>
      updatePreorder(id, data),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: preorderKeys.admin() }),
  });
}

export function useCancelPreorder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => cancelPreorder(id),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: preorderKeys.mine() }),
  });
}
