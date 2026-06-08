"use client";

import { useMemo, useState } from "react";

import { Badge, type BadgeVariant } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { CheckIcon, ChevronRightIcon, CloseIcon, ReceiptIcon } from "@/components/ui/icons";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { H2, Muted } from "@/components/ui/typography";
import { formatRupiah, formatDateTime, formatEstimatedTime } from "@/lib/format";
import { cn } from "@/lib/utils";
import { useMyPreorders } from "@/features/preorder/queries";
import type { Preorder, PreorderStatus } from "@/features/preorder/types";

const statusVariant: Record<PreorderStatus, BadgeVariant> = {
  pending:   "warning",
  confirmed: "success",
  cancelled: "danger",
};

const statusLabel: Record<PreorderStatus, string> = {
  pending:   "Menunggu Konfirmasi",
  confirmed: "Dikonfirmasi",
  cancelled: "Dibatalkan",
};

const queueBadge: Record<string, { label: string; variant: "warning" | "success" | "info" }> = {
  waiting: { label: "Menunggu",  variant: "warning" },
  called:  { label: "Dipanggil", variant: "success" },
  serving: { label: "Dilayani",  variant: "info"    },
};

const tabs = [
  { label: "Semua",        value: ""          },
  { label: "Menunggu",     value: "pending"   },
  { label: "Dikonfirmasi", value: "confirmed" },
  { label: "Dibatalkan",   value: "cancelled" },
];

function getSteps(status: PreorderStatus) {
  if (status === "cancelled") {
    return [
      { key: "pending",   label: "Pesanan Diterima",    done: true,  cancelled: false },
      { key: "cancelled", label: "Pesanan Dibatalkan",  done: false, cancelled: true  },
    ];
  }
  return [
    { key: "pending",   label: "Pesanan Diterima",    done: true,                     cancelled: false },
    { key: "confirmed", label: "Pesanan Dikonfirmasi", done: status === "confirmed",  cancelled: false },
  ];
}

export default function OrderHistoryPage() {
  const [filter, setFilter]     = useState("");
  const [selected, setSelected] = useState<Preorder | null>(null);

  const { data: orders = [], isLoading, isError } = useMyPreorders();

  const filtered = useMemo(
    () => orders.filter((o) => !filter || o.status === filter),
    [orders, filter],
  );

  return (
    <div className="flex flex-col gap-4 px-4 py-5">
      <H2>Pesanan Saya</H2>

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

      {isLoading && (
        <div className="flex flex-col gap-3">
          {Array.from({ length: 3 }).map((_, i) => (
            // biome-ignore lint/suspicious/noArrayIndexKey: skeleton
            <div key={i} className="h-28 animate-pulse rounded-lg bg-muted" />
          ))}
        </div>
      )}

      {isError && <Muted>Gagal memuat pesanan. Coba lagi nanti.</Muted>}

      {!isLoading && !isError && (
        filtered.length === 0 ? (
          <EmptyState
            icon={<ReceiptIcon className="size-6" />}
            title="Belum ada pesanan"
            description="Pesanan akan muncul di sini setelah kamu memesan."
          />
        ) : (
          <div className="flex flex-col gap-3">
            {filtered.map((order) => (
              <button
                key={order.id}
                type="button"
                onClick={() => setSelected(order)}
                className="w-full rounded-lg border border-border bg-card p-4 text-left shadow-sm transition hover:border-primary"
              >
                <div className="flex items-start justify-between">
                  <span className="text-xs text-muted-foreground">
                    {formatDateTime(order.created_at)}
                  </span>
                </div>
                <Badge variant={statusVariant[order.status]} className="mt-1.5">
                  {statusLabel[order.status]}
                </Badge>
                <p className="mt-2 line-clamp-1 text-sm text-muted-foreground">
                  {order.items
                    .map((item) => `${item.quantity}x ${item.menu?.name ?? `Item #${item.menu_item_id.slice(0, 6)}`}`)
                    .join(", ")}
                </p>
                <div className="mt-2 flex items-center justify-between">
                  <span className="font-bold">{formatRupiah(order.total_price)}</span>
                  <span className="flex items-center gap-1 text-xs font-medium text-primary-600">
                    Detail <ChevronRightIcon className="size-3" />
                  </span>
                </div>
              </button>
            ))}
          </div>
        )
      )}

      {/* ── Order detail modal ── */}
      <Modal
        open={!!selected}
        onClose={() => setSelected(null)}
        title={selected ? `Pesanan #${selected.id.slice(0, 8)}` : ""}
        description={selected ? formatDateTime(selected.created_at) : undefined}
        footer={<Button variant="ghost" onClick={() => setSelected(null)}>Tutup</Button>}
      >
        {selected && (
          <div className="flex flex-col gap-4">
            <Badge variant={statusVariant[selected.status]}>
              {statusLabel[selected.status]}
            </Badge>

            {/* Queue card — only shown when data is still meaningful */}
            {selected.queue?.queue_number != null && selected.status !== "cancelled" && (() => {
              const q = selected.queue;
              const isPending = selected.status === "pending";

              if (isPending) {
                const badge = queueBadge[q.status] ?? { label: q.status, variant: "info" as const };
                return (
                  <Card>
                    <CardContent className="flex flex-col items-center gap-2 py-4 text-center">
                      <span className="text-4xl font-bold tracking-tight text-primary-600">
                        #{q.queue_number}
                      </span>
                      <Muted>Nomor tiket antrian kamu</Muted>
                      <Badge variant={badge.variant}>{badge.label}</Badge>
                      {q.estimated_time && (
                        <div className="mt-1 w-full rounded-md bg-muted p-2">
                          <span className="text-xs text-muted-foreground">Estimasi selesai</span>
                          <p className="text-lg font-bold">{formatEstimatedTime(q.estimated_time)}</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              }

              // confirmed: show queue number as a static reference only
              return (
                <div className="flex items-center gap-2 rounded-lg bg-muted px-3 py-2">
                  <span className="text-xs text-muted-foreground">Nomor Tiket</span>
                  <span className="font-mono font-bold text-primary-600">#{q.queue_number}</span>
                </div>
              );
            })()}

            {/* Status steps */}
            <div className="flex flex-col gap-3">
              <span className="text-xs font-medium text-muted-foreground">Status</span>
              {getSteps(selected.status).map((step) => (
                <div key={step.key} className="flex items-center gap-2 text-sm">
                  <span className={cn(
                    "flex size-6 shrink-0 items-center justify-center rounded-full",
                    step.done && !step.cancelled && "bg-success text-success-foreground",
                    step.cancelled && "bg-destructive text-destructive-foreground",
                    !step.done && !step.cancelled && "border-2 border-muted-foreground/30 bg-card",
                  )}>
                    {step.done && !step.cancelled && <CheckIcon className="size-3.5" />}
                    {step.cancelled && <CloseIcon className="size-3.5" />}
                  </span>
                  <span className={cn(
                    step.cancelled && "text-destructive",
                    !step.done && !step.cancelled && "text-muted-foreground",
                  )}>
                    {step.label}
                  </span>
                </div>
              ))}
            </div>

            {/* Items */}
            <div className="flex flex-col gap-2">
              <span className="text-xs font-medium text-muted-foreground">Item</span>
              {selected.items.map((item, idx) => (
                // biome-ignore lint/suspicious/noArrayIndexKey: stable order items
                <div key={idx} className="flex items-center justify-between text-sm">
                  <span>
                    {item.quantity}x {item.menu?.name ?? `Item #${item.menu_item_id}`}
                  </span>
                  <span className="font-medium">{formatRupiah(item.subtotal)}</span>
                </div>
              ))}
              <hr className="border-border" />
              <div className="flex items-center justify-between font-bold text-sm">
                <span>Total</span>
                <span>{formatRupiah(selected.total_price)}</span>
              </div>
            </div>

            {selected.notes && (
              <p className="text-xs text-muted-foreground">
                Catatan: {selected.notes}
              </p>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
