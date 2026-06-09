import Link from "next/link";

import {
  BellIcon,
  DashboardIcon,
  MenuBookIcon,
  QueueIcon,
  ReceiptIcon,
  SettingsIcon,
  TagIcon,
} from "./icons";
import { type NavItem, SidebarNav } from "./sidebar-nav";

const adminNav: NavItem[] = [
  {
    href: "/admin/dashboard",
    label: "Dashboard",
    icon: <DashboardIcon className="size-5" />,
  },
  {
    href: "/admin/queues",
    label: "Antrian",
    icon: <QueueIcon className="size-5" />,
  },
  {
    href: "/admin/preorders",
    label: "Pre-order",
    icon: <ReceiptIcon className="size-5" />,
  },
  {
    href: "/admin/menu",
    label: "Menu",
    icon: <MenuBookIcon className="size-5" />,
  },
  {
    href: "/admin/statuses",
    label: "Status Antrian",
    icon: <TagIcon className="size-5" />,
  },
  {
    href: "/admin/settings",
    label: "Pengaturan",
    icon: <SettingsIcon className="size-5" />,
  },
];

/** Admin sidebar shell: brand + primary navigation. */
export function Sidebar() {
  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-border bg-card lg:flex">
      <Link
        href="/admin/dashboard"
        className="flex h-16 items-center gap-2 border-b border-border px-5"
      >
        <span className="flex size-8 items-center justify-center rounded-md bg-primary font-bold text-primary-foreground">
          A
        </span>
        <span className="text-lg font-bold tracking-tight">AntreIn</span>
        <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] font-semibold text-muted-foreground">
          ADMIN
        </span>
      </Link>
      <div className="flex-1 overflow-y-auto p-3">
        <SidebarNav items={adminNav} />
      </div>
      <div className="border-t border-border p-3">
        <Link
          href="/menu"
          className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground transition hover:bg-accent hover:text-foreground"
        >
          <BellIcon className="size-4" />
          Lihat sisi customer
        </Link>
      </div>
    </aside>
  );
}
