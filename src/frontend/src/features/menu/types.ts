import { z } from "zod";

/** Mirrors menu-preorder-service Menu model & enums. */

export type MenuCategory = "makanan" | "minuman" | "snacks";

export const MENU_CATEGORIES: { label: string; value: MenuCategory }[] = [
  { label: "Makanan", value: "makanan" },
  { label: "Minuman", value: "minuman" },
  { label: "Camilan", value: "snacks" },
];

export interface MenuItem {
  id: string;
  name: string;
  description: string | null;
  price: number;
  category: MenuCategory;
  is_available: boolean;
  is_deleted: boolean;
  created_at: string;
  updated_at: string | null;
}

export const menuSchema = z.object({
  name: z.string().min(1, "Nama menu wajib diisi").max(100, "Maks 100 karakter"),
  description: z.string().max(255, "Maks 255 karakter").optional().or(z.literal("")),
  price: z.number().positive("Harga harus lebih dari 0"),
  category: z.enum(["makanan", "minuman", "snacks"]),
  is_available: z.boolean(),
});
export type MenuValues = z.infer<typeof menuSchema>;
