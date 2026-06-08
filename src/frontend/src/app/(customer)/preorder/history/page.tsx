"use client";

import { useMemo, useState } from "react";

import { Badge, type BadgeVariant } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { ReceiptIcon } from "@/components/ui/icons";
import { Button } from "@/components/ui/button";
import { H2 } from "@/components/ui/typography";
import { formatRupiah } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { PreorderStatus } from "@/features/preorder/types";

const statusVariant: Record<PreorderStatus, BadgeVariant> = {
  pending: "warning",
  confirmed: "success",
  cancelled: "danger",
};

const statusLabel: Record<PreorderStatus, string> = {
  pending: "Menunggu",
  confirmed: "Dikonfirmasi",
  cancelled: "Dibatalkan",
};

const tabs = [
  { label: "Semua", value: "" },
  { label: "Menunggu", value: "pending" },
  { label: "Dikonfirmasi", value: "confirmed" },
  { label: "Dibatalkan", value: "cancelled" },
];

const mockHistory = [
  { id: "ORD-2024-0042", status: "pending" as PreorderStatus, items: "2x Nasi Goreng, 1x Es Teh", total: 66000, date: "15 Jan 2026, 10:32" },
  { id: "ORD-2024-0041", status: "confirmed" as PreorderStatus, items: "1x Mie Ayam, 1x Es Jeruk", total: 37000, date: "15 Jan 2026, 09:15" },
  { id: "ORD-2024-0040", status: "confirmed" as PreorderStatus, items: "1x Ayam Geprek, 2x Es Teh", total: 44000, date: "14 Jan 2026, 18:45" },
  { id: "ORD-2024-0039", status: "cancelled" as PreorderStatus, items: "1x Soto Ayam", total: 27000, date: "14 Jan 2026, 12:10" },
  { id: "ORD-2024-0038", status: "confirmed" as PreorderStatus, items: "3x Pisang Goreng, 2x Kopi Susu", total: 81000, date: "13 Jan 2026, 16:30" },
];

export default function OrderHistoryPage() {
  const [filter, setFilter] = useState("");

  const filtered = useMemo(
    () => mockHistory.filter((o) => !filter || o.status === filter),
    [filter],
  );

  return (
    <div className="flex flex-col gap-4 px-4 py-5">
      <H2>Riwayat Pesanan</H2>

      <div className="flex gap-2 overflow-x-auto pb-1">
        {tabs.map((tab) => (
          <button
            key={tab.value}
            type="button"
            onClick={() => setFilter(tab.value)}
            className={cn(
              "shrink-0 rounded-full px-4 py-1.5 text-sm font-medium transition",
              filter === tab.value
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-accent hover:text-foreground",
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={<ReceiptIcon className="size-6" />}
          title="Belum ada pesanan"
          description="Pesanan akan muncul di sini setelah kamu memesan."
        />
      ) : (
        <div className="flex flex-col gap-3">
          {filtered.map((order) => (
            <div
              key={order.id}
              className="rounded-lg border border-border bg-card p-4 shadow-sm"
            >
              <div className="flex items-start justify-between">
                <span className="text-xs font-mono font-semibold">{order.id}</span>
                <span className="text-xs text-muted-foreground">{order.date}</span>
              </div>
              <Badge variant={statusVariant[order.status]} className="mt-1">
                {statusLabel[order.status]}
              </Badge>
              <p className="mt-2 line-clamp-1 text-sm">{order.items}</p>
              <div className="mt-2 flex items-center justify-between">
                <span className="font-bold">{formatRupiah(order.total)}</span>
                {order.status === "cancelled" && (
                  <Button variant="outline" size="sm">
                    Pesan Lagi
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
