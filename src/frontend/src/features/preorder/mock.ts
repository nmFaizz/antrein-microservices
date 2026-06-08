import { mockMenu } from "@/features/menu/mock";

import type { Preorder } from "./types";

const TODAY = "2026-06-08";
const menu = (id: string) => mockMenu.find((m) => m.id === id) ?? null;

/** Mock preorders — delete on integration. */
export const mockPreorders: Preorder[] = [
  {
    id: "p1",
    user_id: "u1",
    notes: "Tidak pakai sambal",
    total_price: 56000,
    status: "confirmed",
    created_at: `${TODAY}T07:08:00Z`,
    updated_at: `${TODAY}T07:10:00Z`,
    customer_name: "Budi Santoso",
    items: [
      { menu_item_id: "m1", quantity: 2, subtotal: 56000, menu: menu("m1") },
    ],
    queue: {
      id: "q1",
      queue_number: "A001",
      position: 0,
      estimated_time: `${TODAY}T07:30:00Z`,
      status: "served",
    },
  },
  {
    id: "p2",
    user_id: "u2",
    notes: null,
    total_price: 45000,
    status: "confirmed",
    created_at: `${TODAY}T07:11:00Z`,
    updated_at: `${TODAY}T07:12:00Z`,
    customer_name: "Siti Aminah",
    items: [
      { menu_item_id: "m3", quantity: 1, subtotal: 32000, menu: menu("m3") },
      { menu_item_id: "m7", quantity: 1, subtotal: 18000, menu: menu("m7") },
    ],
    queue: {
      id: "q2",
      queue_number: "A002",
      position: 0,
      estimated_time: `${TODAY}T07:40:00Z`,
      status: "called",
    },
  },
  {
    id: "p3",
    user_id: "u3",
    notes: "Pedas level 2",
    total_price: 33000,
    status: "pending",
    created_at: `${TODAY}T07:14:00Z`,
    updated_at: null,
    customer_name: "Andi Wijaya",
    items: [
      { menu_item_id: "m2", quantity: 1, subtotal: 25000, menu: menu("m2") },
      { menu_item_id: "m5", quantity: 1, subtotal: 8000, menu: menu("m5") },
    ],
    queue: {
      id: "q3",
      queue_number: "A003",
      position: 1,
      estimated_time: `${TODAY}T07:44:00Z`,
      status: "waiting",
    },
  },
  {
    id: "p7",
    user_id: "u7",
    notes: null,
    total_price: 20000,
    status: "cancelled",
    created_at: `${TODAY}T07:25:00Z`,
    updated_at: `${TODAY}T07:30:00Z`,
    customer_name: "Joko Susilo",
    items: [
      { menu_item_id: "m6", quantity: 1, subtotal: 12000, menu: menu("m6") },
      { menu_item_id: "m5", quantity: 1, subtotal: 8000, menu: menu("m5") },
    ],
    queue: null,
  },
];
