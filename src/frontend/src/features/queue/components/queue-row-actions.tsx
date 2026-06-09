"use client";

import { Button } from "@/components/ui/button";

import type { Queue } from "../types";

export type QueueAction = "call" | "serve" | "skip" | "requeue" | "cancel";

/** Which actions are available for a given status (mirrors ALLOWED_TRANSITIONS). */
export function actionsForStatus(status: string): QueueAction[] {
  switch (status) {
    case "waiting":
      return ["call", "skip", "cancel"];
    case "called":
      return ["serve", "skip"];
    case "skipped":
      return ["requeue"];
    default:
      return [];
  }
}

const labels: Record<QueueAction, string> = {
  call: "Panggil",
  serve: "Selesai",
  skip: "Lewati",
  requeue: "Re-queue",
  cancel: "Batal",
};

interface QueueRowActionsProps {
  queue: Queue;
  onAction: (queue: Queue, action: QueueAction) => void;
}

/** Per-row action buttons; visible set depends on the queue's status. */
export function QueueRowActions({ queue, onAction }: QueueRowActionsProps) {
  const actions = actionsForStatus(queue.status_name);
  if (!actions.length) {
    return <span className="text-xs text-muted-foreground">—</span>;
  }

  return (
    <div className="flex items-center justify-end gap-1.5">
      {actions.map((action) => (
        <Button
          key={action}
          size="sm"
          variant={
            action === "call" || action === "serve"
              ? "primary"
              : action === "cancel"
                ? "destructive"
                : "outline"
          }
          onClick={() => onAction(queue, action)}
        >
          {labels[action]}
        </Button>
      ))}
    </div>
  );
}

/** Confirm-dialog copy + resulting status for each action. */
export const actionMeta: Record<
  QueueAction,
  {
    title: string;
    description: string;
    nextStatus: string;
    variant: "primary" | "destructive";
  }
> = {
  call: {
    title: "Panggil antrian ini?",
    description:
      "Status akan berubah menjadi 'called' dan grace period dimulai.",
    nextStatus: "called",
    variant: "primary",
  },
  serve: {
    title: "Tandai selesai dilayani?",
    description: "Status akan berubah menjadi 'served'.",
    nextStatus: "served",
    variant: "primary",
  },
  skip: {
    title: "Lewati antrian ini?",
    description: "Status akan berubah menjadi 'skipped' (no-show).",
    nextStatus: "skipped",
    variant: "destructive",
  },
  requeue: {
    title: "Buat ulang antrian (re-queue)?",
    description: "Antrian baru dibuat di belakang dengan status 'waiting'.",
    nextStatus: "re_queued",
    variant: "primary",
  },
  cancel: {
    title: "Batalkan antrian ini?",
    description: "Status akan berubah menjadi 'cancelled'. Tindakan ini final.",
    nextStatus: "cancelled",
    variant: "destructive",
  },
};
