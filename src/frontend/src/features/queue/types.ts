import { z } from "zod";

/** Mirrors backend queue-service models & enums (no API binding yet). */

export const QUEUE_STATUSES = [
  "waiting",
  "called",
  "served",
  "skipped",
  "re_queued",
  "cancelled",
] as const;
export type QueueStatusName = (typeof QUEUE_STATUSES)[number];

export type TriggerType = "admin" | "customer" | "system";

export type NotificationType =
  | "confirmation"
  | "prepare"
  | "almost"
  | "called"
  | "skipped"
  | "requeued";

export type NotificationStatus = "pending" | "sent" | "failed";

/** Default colors from backend `DEFAULT_STATUS_COLORS`. */
export const STATUS_COLORS: Record<string, string> = {
  waiting: "#9CA3AF",
  called: "#3B82F6",
  served: "#10B981",
  skipped: "#F97316",
  re_queued: "#8B5CF6",
  cancelled: "#EF4444",
};

export interface QueueStatus {
  id: string;
  name: string;
  color: string | null;
}

/** Mirrors `QueueRead` (includes computed position + wait). */
export interface Queue {
  id: string;
  user_id: string;
  preorder_id: string | null;
  queue_number: number;
  queue_date: string;
  estimated_time: string | null;
  is_checked_in: boolean;
  checked_in_at: string | null;
  status_id: string;
  status_name: string;
  called_at: string | null;
  served_at: string | null;
  cancelled_at: string | null;
  called_by: string | null;
  served_by: string | null;
  skipped_by: string | null;
  is_requeued: boolean;
  original_queue_id: string | null;
  created_at: string;
  updated_at: string;
  current_position: number;
  estimated_wait_minutes: number;
  /** Denormalized for display only (would come from User Service). */
  customer_name?: string;
}

export interface QueueStatusLog {
  id: string;
  queue_id: string;
  previous_status: string | null;
  new_status: string;
  triggered_by: string | null;
  trigger_type: TriggerType;
  notes: string | null;
  created_at: string;
}

export interface QueueNotification {
  id: string;
  name: string | null;
  queue_id: string;
  customer_id: string;
  notification_type: NotificationType;
  status: NotificationStatus;
  message: string | null;
  sent_at: string | null;
  failed_reason: string | null;
  created_at: string;
}

export interface QueueSettings {
  id: string;
  prefix: string;
  grace_period_mins: number;
  avg_serve_time_mins: number;
  max_queue_per_day: number;
  is_queue_open: boolean;
  open_time: string | null;
  close_time: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

/** Format "A" + 1 → "A001". */
export function formatQueueNumber(prefix: string, n: number): string {
  return `${prefix}${String(n).padStart(3, "0")}`;
}

// --- Form schemas -----------------------------------------------------------

export const queueSettingsSchema = z.object({
  prefix: z.string().min(1, "Prefix wajib diisi").max(3, "Maks 3 karakter"),
  grace_period_mins: z.number().int().min(0, "Tidak boleh negatif"),
  avg_serve_time_mins: z.number().int().min(1, "Minimal 1 menit"),
  max_queue_per_day: z.number().int().min(1, "Minimal 1"),
  is_queue_open: z.boolean(),
  open_time: z.string().min(1, "Jam buka wajib diisi"),
  close_time: z.string().min(1, "Jam tutup wajib diisi"),
});
export type QueueSettingsValues = z.infer<typeof queueSettingsSchema>;

export const queueStatusSchema = z.object({
  name: z.string().min(1, "Nama status wajib diisi"),
  color: z
    .string()
    .regex(/^#([0-9a-fA-F]{6})$/, "Gunakan format hex, mis. #FACC15"),
});
export type QueueStatusValues = z.infer<typeof queueStatusSchema>;

// --- API payloads (mirror backend Create/Update schemas) --------------------

/** Body for `POST /queue-settings` (`created_by` = admin user id). */
export interface QueueSettingsCreatePayload {
  prefix: string;
  grace_period_mins: number;
  avg_serve_time_mins: number;
  max_queue_per_day: number;
  is_queue_open: boolean;
  open_time: string | null;
  close_time: string | null;
  created_by: string;
}

/** Body for `PATCH /queue-settings/{id}` (all optional). */
export type QueueSettingsUpdatePayload = Partial<
  Omit<QueueSettingsCreatePayload, "created_by">
>;

/** Body for `POST /queue-statuses`. */
export interface QueueStatusCreatePayload {
  name: string;
  color?: string | null;
}

/** Body for `PATCH /queue-statuses/{id}` (all optional). */
export type QueueStatusUpdatePayload = Partial<QueueStatusCreatePayload>;
