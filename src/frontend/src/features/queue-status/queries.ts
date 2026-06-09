import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type {
  QueueStatusCreatePayload,
  QueueStatusUpdatePayload,
} from "@/features/queue/types";

import { createStatus, deleteStatus, getStatuses, updateStatus } from "./api";

export const statusKeys = {
  all: ["queue-statuses"] as const,
};

export function useStatuses() {
  return useQuery({
    queryKey: statusKeys.all,
    queryFn: getStatuses,
  });
}

export function useCreateStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: QueueStatusCreatePayload) => createStatus(payload),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: statusKeys.all }),
  });
}

export function useUpdateStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: string;
      payload: QueueStatusUpdatePayload;
    }) => updateStatus(id, payload),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: statusKeys.all }),
  });
}

export function useDeleteStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteStatus(id),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: statusKeys.all }),
  });
}
