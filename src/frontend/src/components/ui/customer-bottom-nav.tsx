"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

import { useCart } from "./cart-provider";
import { CartIcon, MenuBookIcon, ReceiptIcon } from "./icons";

interface CustomerNavItem {
  href: string;
  label: string;
  icon: ReactNode;
  badge?: number;
}

/** Customer bottom tab bar with a live cart badge. */
export function CustomerBottomNav() {
  const pathname = usePathname();
  const { itemCount } = useCart();

  const items = [
    {
      href: "/menu",
      label: "Menu",
      icon: <MenuBookIcon className="size-5" />,
      active: pathname === "/menu",
    },
    {
      href: "/preorder",
      label: "Keranjang",
      icon: <CartIcon className="size-5" />,
      active: pathname === "/preorder",
      badge: itemCount,
    },
    {
      href: "/preorder/history",
      label: "Pesanan",
      icon: <ReceiptIcon className="size-5" />,
      active: pathname === "/preorder/history",
    },
  ];

  return (
    <nav className="sticky bottom-0 z-30 grid grid-cols-3 border-t border-border bg-card/95 backdrop-blur">
      {items.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={cn(
            "flex flex-col items-center gap-1 py-2.5 text-xs font-medium transition",
            item.active
              ? "text-primary-600"
              : "text-muted-foreground hover:text-foreground",
          )}
        >
          <span className="relative">
            {item.icon}
            {item.badge ? (
              <span className="absolute -right-2 -top-1.5 flex min-w-4 items-center justify-center rounded-full bg-primary px-1 text-[10px] font-bold text-primary-foreground">
                {item.badge}
              </span>
            ) : null}
          </span>
          {item.label}
        </Link>
      ))}
    </nav>
  );
}
