import type { MenuItem } from "@/features/menu/types";

/** Mirrors menu-preorder-service Preorder models & enums. */

export type PreorderStatus = "pending" | "confirmed" | "cancelled";

export interface PreorderItem {
  menu_item_id: string;
  quantity: number;
  subtotal: number;
  menu?: MenuItem | null;
}

/** Queue snapshot stored on the preorder (JSON from queue-service). */
export interface PreorderQueueInfo {
  id: string;
  queue_number: string;
  position: number;
  estimated_time: string | null;
  status: string;
}

export interface Preorder {
  id: string;
  user_id: string;
  notes: string | null;
  total_price: number;
  status: PreorderStatus;
  created_at: string;
  updated_at: string | null;
  items: PreorderItem[];
  queue: PreorderQueueInfo | null;
  /** Denormalized for display only. */
  customer_name?: string;
}
