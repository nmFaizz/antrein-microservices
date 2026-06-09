import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { preorderKeys } from "@/features/preorder/queries";

import {
  callNext,
  cancelQueue,
  checkInQueue,
  getQueue,
  getQueueLogs,
  getQueueNotifications,
  getQueues,
  requeueQueue,
  serveQueue,
  skipQueue,
} from "./api";

export const queueKeys = {
  all: ["queues"] as const,
  list: (params?: { queue_date?: string }) =>
    [...queueKeys.all, "list", params] as const,
  detail: (id: string) => [...queueKeys.all, "detail", id] as const,
  logs: (id: string) => [...queueKeys.all, "logs", id] as const,
  notifications: (id: string) =>
    [...queueKeys.all, "notifications", id] as const,
};

export function useQueues(params?: { queue_date?: string }) {
  return useQuery({
    queryKey: queueKeys.list(params),
    queryFn: () => getQueues(params),
  });
}

export function useQueue(
  id: string | undefined,
  options?: { refetchInterval?: number },
) {
  return useQuery({
    queryKey: queueKeys.detail(id ?? ""),
    queryFn: () => getQueue(id as string),
    enabled: !!id,
    refetchInterval: options?.refetchInterval,
  });
}

export function useQueueLogs(id: string | undefined) {
  return useQuery({
    queryKey: queueKeys.logs(id ?? ""),
    queryFn: () => getQueueLogs(id as string),
    enabled: !!id,
  });
}

export function useQueueNotifications(id: string | undefined) {
  return useQuery({
    queryKey: queueKeys.notifications(id ?? ""),
    queryFn: () => getQueueNotifications(id as string),
    enabled: !!id,
  });
}

export function useCheckIn() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => checkInQueue(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queueKeys.all });
      queryClient.invalidateQueries({ queryKey: preorderKeys.all });
    },
  });
}

export function useCallNext() {
  const queryClient = useQueryClient();
  return useMutation({
    // Call next for today; `mutate()` takes no argument.
    mutationFn: () => callNext(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queueKeys.all }),
  });
}

export function useServeQueue() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => serveQueue(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queueKeys.all });
      // serve auto-confirms the linked preorder on the backend
      queryClient.invalidateQueries({ queryKey: preorderKeys.all });
    },
  });
}

export function useSkipQueue() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, notes }: { id: string; notes?: string }) =>
      skipQueue(id, notes),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queueKeys.all }),
  });
}

export function useRequeueQueue() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => requeueQueue(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queueKeys.all }),
  });
}

export function useCancelQueue() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => cancelQueue(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queueKeys.all });
      // cancel also updates the linked preorder to "cancelled"
      queryClient.invalidateQueries({ queryKey: preorderKeys.all });
    },
  });
}
