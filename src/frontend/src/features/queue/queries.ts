import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { preorderKeys } from "@/features/preorder/queries";

import {
  callNext,
  cancelQueue,
  getQueues,
  requeueQueue,
  serveQueue,
  skipQueue,
} from "./api";

export const queueKeys = {
  all: ["queues"] as const,
  list: (params?: { queue_date?: string }) =>
    [...queueKeys.all, "list", params] as const,
};

export function useQueues(params?: { queue_date?: string }) {
  return useQuery({
    queryKey: queueKeys.list(params),
    queryFn: () => getQueues(params),
  });
}

export function useCallNext() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (queue_date?: string) => callNext(queue_date),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: queueKeys.all }),
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
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: queueKeys.all }),
  });
}

export function useRequeueQueue() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => requeueQueue(id),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: queueKeys.all }),
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
