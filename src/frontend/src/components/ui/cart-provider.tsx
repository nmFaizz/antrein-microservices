"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";

import type { MenuItem } from "@/features/menu/types";

export interface CartLine {
  menu: MenuItem;
  quantity: number;
}

interface CartContextValue {
  lines: CartLine[];
  itemCount: number;
  total: number;
  add: (menu: MenuItem) => void;
  setQuantity: (menuId: string, quantity: number) => void;
  remove: (menuId: string) => void;
  clear: () => void;
}

const CartContext = createContext<CartContextValue | null>(null);

/**
 * In-memory cart for the customer preorder flow. No persistence / no API —
 * integration-ready: swap this for a server cart or mutation later.
 */
export function CartProvider({ children }: { children: React.ReactNode }) {
  const [lines, setLines] = useState<CartLine[]>([]);

  const add = useCallback((menu: MenuItem) => {
    setLines((prev) => {
      const existing = prev.find((line) => line.menu.id === menu.id);
      if (existing) {
        return prev.map((line) =>
          line.menu.id === menu.id
            ? { ...line, quantity: line.quantity + 1 }
            : line,
        );
      }
      return [...prev, { menu, quantity: 1 }];
    });
  }, []);

  const setQuantity = useCallback((menuId: string, quantity: number) => {
    setLines((prev) =>
      quantity <= 0
        ? prev.filter((line) => line.menu.id !== menuId)
        : prev.map((line) =>
            line.menu.id === menuId ? { ...line, quantity } : line,
          ),
    );
  }, []);

  const remove = useCallback((menuId: string) => {
    setLines((prev) => prev.filter((line) => line.menu.id !== menuId));
  }, []);

  const clear = useCallback(() => setLines([]), []);

  const value = useMemo<CartContextValue>(() => {
    const itemCount = lines.reduce((sum, line) => sum + line.quantity, 0);
    const total = lines.reduce(
      (sum, line) => sum + line.menu.price * line.quantity,
      0,
    );
    return { lines, itemCount, total, add, setQuantity, remove, clear };
  }, [lines, add, setQuantity, remove, clear]);

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used inside <CartProvider>");
  return ctx;
}
