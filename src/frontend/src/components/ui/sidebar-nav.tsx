"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export interface NavItem {
  href: string;
  label: string;
  icon: ReactNode;
  badge?: number;
}

/** Vertical nav list with active-route highlighting (via `usePathname`). */
export function SidebarNav({ items }: { items: NavItem[] }) {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-1">
      {items.map((item) => {
        const active =
          pathname === item.href || pathname.startsWith(`${item.href}/`);
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition",
              active
                ? "bg-primary text-primary-foreground"
                : "text-foreground/70 hover:bg-accent hover:text-foreground",
            )}
          >
            <span className="shrink-0">{item.icon}</span>
            <span className="flex-1">{item.label}</span>
            {item.badge ? (
              <span className="flex min-w-5 items-center justify-center rounded-full bg-destructive px-1.5 py-0.5 text-[11px] font-bold text-destructive-foreground">
                {item.badge}
              </span>
            ) : null}
          </Link>
        );
      })}
    </nav>
  );
}
