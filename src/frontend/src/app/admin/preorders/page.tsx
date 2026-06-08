"use client";

import { useMemo, useState } from "react";

import { Badge, type BadgeVariant } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { FilterSelect } from "@/components/ui/filter-select";
import { ChevronRightIcon, CloseIcon, ReceiptIcon } from "@/components/ui/icons";
import { Modal } from "@/components/ui/modal";
import { PageHeader } from "@/components/ui/page-header";
import { SearchInput } from "@/components/ui/search-input";
import { Button } from "@/components/ui/button";
import { Muted } from "@/components/ui/typography";
import { formatRupiah, formatTime } from "@/lib/format";
import { cn } from "@/lib/utils";
import { useAllPreorders, useUpdatePreorder } from "@/features/preorder/queries";
import type { Preorder, PreorderStatus } from "@/features/preorder/types";

const statusVariant: Record<PreorderStatus, BadgeVariant> = {
  pending:   "warning",
  confirmed: "success",
  cancelled: "danger",
};

const statusLabel: Record<PreorderStatus, string> = {
  pending:   "Menunggu",
  confirmed: "Dikonfirmasi",
  cancelled: "Dibatalkan",
};

const filterOptions = [
  { label: "Semua",        value: ""          },
  { label: "Menunggu",     value: "pending"   },
  { label: "Dikonfirmasi", value: "confirmed" },
  { label: "Dibatalkan",   value: "cancelled" },
];

function displayName(order: Preorder): string {
  return order.customer_name ?? `#${order.user_id.slice(0, 8)}`;
}

export default function AdminPreordersPage() {
  const [search, setSearch]     = useState("");
  const [status, setStatus]     = useState("");
  const [selected, setSelected] = useState<Preorder | null>(null);

  const { data: orders = [], isLoading, isError } = useAllPreorders();
  const updatePreorder = useUpdatePreorder();

  const filtered = useMemo(() => {
    return orders.filter((o) => {
      const matchSearch =
        !search ||
        o.id.toLowerCase().includes(search.toLowerCase()) ||
        (o.customer_name ?? "").toLowerCase().includes(search.toLowerCase());
      const matchStatus = !status || o.status === status;
      return matchSearch && matchStatus;
    });
  }, [orders, search, status]);

  const pendingCount = orders.filter((o) => o.status === "pending").length;

  async function updateStatus(id: string, newStatus: PreorderStatus) {
    await updatePreorder.mutateAsync({ id, data: { status: newStatus } });
    if (selected?.id === id) setSelected((prev) => prev ? { ...prev, status: newStatus } : null);
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Daftar Pesanan"
        subtitle={`${orders.length} total · ${pendingCount} menunggu konfirmasi`}
      />

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <SearchInput
          className="sm:max-w-xs"
          placeholder="Cari pesanan…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <FilterSelect
          options={filterOptions}
          placeholder="Semua status"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        />
      </div>

      {/* ── Loading skeletons ── */}
      {isLoading && (
        <div className="flex flex-col gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            // biome-ignore lint/suspicious/noArrayIndexKey: skeleton
            <div key={i} className="h-24 animate-pulse rounded-lg bg-muted" />
          ))}
        </div>
      )}

      {isError && <Muted>Gagal memuat pesanan. Coba lagi nanti.</Muted>}

      {/* ── Mobile cards ── */}
      {!isLoading && !isError && (
        <>
          {filtered.length === 0 ? (
            <EmptyState
              icon={<ReceiptIcon className="size-6" />}
              title="Tidak ada pesanan"
              description="Belum ada pesanan masuk."
            />
          ) : (
            <div className="flex flex-col gap-3 lg:hidden">
              {filtered.map((order) => (
                <button
                  key={order.id}
                  type="button"
                  onClick={() => setSelected(order)}
                  className="w-full rounded-lg border border-border bg-card p-4 text-left shadow-sm transition hover:border-primary"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      {order.queue?.queue_number != null && (
                        <span className="flex size-7 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground">
                          {order.queue.queue_number}
                        </span>
                      )}
                      <span className="font-mono text-xs font-semibold text-muted-foreground">
                        #{order.id.slice(0, 8)}
                      </span>
                    </div>
                    <Badge variant={statusVariant[order.status]}>
                      {statusLabel[order.status]}
                    </Badge>
                  </div>
                  <p className="mt-1 text-sm font-medium">{displayName(order)}</p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {order.items.length} item · {formatRupiah(order.total_price)}
                  </p>
                  <div className="mt-2 flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">
                      {formatTime(order.created_at)}
                    </span>
                    <span className="flex items-center gap-1 text-xs font-medium text-primary-600">
                      Detail <ChevronRightIcon className="size-3" />
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* ── Desktop table ── */}
          <div className="hidden overflow-hidden rounded-lg border border-border lg:block">
            <table className="w-full text-sm">
              <thead className="border-b border-border bg-muted">
                <tr>
                  {["Antrian", "ID", "Pelanggan", "Item", "Total", "Status", "Waktu", "Aksi"].map((h) => (
                    <th key={h} className="px-4 py-2.5 text-left font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-4 py-10 text-center">
                      <Muted>Tidak ada pesanan.</Muted>
                    </td>
                  </tr>
                ) : (
                  filtered.map((order) => (
                    <tr key={order.id} className="border-b border-border last:border-0">
                      <td className="px-4 py-2.5 text-center">
                        {order.queue?.queue_number != null ? (
                          <span className="inline-flex size-7 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground">
                            {order.queue.queue_number}
                          </span>
                        ) : (
                          <span className="text-xs text-muted-foreground">—</span>
                        )}
                      </td>
                      <td className="px-4 py-2.5 font-mono text-xs text-muted-foreground">
                        #{order.id.slice(0, 8)}
                      </td>
                      <td className="px-4 py-2.5 font-medium">{displayName(order)}</td>
                      <td className="px-4 py-2.5 text-muted-foreground">
                        {order.items.length} item
                      </td>
                      <td className="px-4 py-2.5 font-medium">
                        {formatRupiah(order.total_price)}
                      </td>
                      <td className="px-4 py-2.5">
                        <Badge variant={statusVariant[order.status]}>
                          {statusLabel[order.status]}
                        </Badge>
                      </td>
                      <td className="px-4 py-2.5 text-muted-foreground">
                        {formatTime(order.created_at)}
                      </td>
                      <td className="px-4 py-2.5">
                        <div className="flex gap-1">
                          {order.status === "pending" && (
                            <>
                              <Button
                                size="sm"
                                disabled={updatePreorder.isPending}
                                onClick={() => updateStatus(order.id, "confirmed")}
                              >
                                Konfirmasi
                              </Button>
                              <Button
                                size="sm"
                                variant="destructive"
                                disabled={updatePreorder.isPending}
                                onClick={() => updateStatus(order.id, "cancelled")}
                              >
                                Batalkan
                              </Button>
                            </>
                          )}
                          {order.status === "confirmed" && (
                            <Button
                              size="sm"
                              variant="destructive"
                              disabled={updatePreorder.isPending}
                              onClick={() => updateStatus(order.id, "cancelled")}
                            >
                              Batalkan
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* ── Detail modal ── */}
      <Modal
        open={!!selected}
        onClose={() => setSelected(null)}
        title={selected ? `#${selected.id.slice(0, 8)}` : ""}
        description={selected ? displayName(selected) : undefined}
        footer={
          selected?.status === "pending" ? (
            <>
              <Button
                variant="destructive"
                disabled={updatePreorder.isPending}
                onClick={() => { updateStatus(selected.id, "cancelled"); setSelected(null); }}
              >
                Batalkan Pesanan
              </Button>
              <Button
                disabled={updatePreorder.isPending}
                onClick={() => { updateStatus(selected.id, "confirmed"); setSelected(null); }}
              >
                Konfirmasi Pesanan
              </Button>
            </>
          ) : selected?.status === "confirmed" ? (
            <>
              <Button variant="ghost" onClick={() => setSelected(null)}>Tutup</Button>
              <Button
                variant="destructive"
                disabled={updatePreorder.isPending}
                onClick={() => { updateStatus(selected.id, "cancelled"); setSelected(null); }}
              >
                Batalkan Pesanan
              </Button>
            </>
          ) : (
            <Button variant="ghost" onClick={() => setSelected(null)}>Tutup</Button>
          )
        }
      >
        {selected && (
          <div className="flex flex-col gap-4">
            <div className="flex flex-wrap items-center gap-2">
              {selected.queue?.queue_number != null && (
                <div className="flex items-center gap-2 rounded-lg bg-primary/10 px-3 py-1.5">
                  <span className="text-xs font-medium text-muted-foreground">Nomor Antrian</span>
                  <span className="text-lg font-bold text-primary-600">
                    #{selected.queue.queue_number}
                  </span>
                </div>
              )}
              <Badge variant={statusVariant[selected.status]}>
                {statusLabel[selected.status]}
              </Badge>
              {selected.notes && (
                <span className="text-xs text-muted-foreground">
                  Catatan: {selected.notes}
                </span>
              )}
            </div>

            <div className="flex flex-col gap-2">
              <span className="text-xs font-medium text-muted-foreground">Status</span>
              {[
                { key: "pending",   label: "Pesanan Diterima"    },
                { key: "confirmed", label: "Pesanan Dikonfirmasi" },
              ].map((step) => {
                const done =
                  (step.key === "pending" && selected.status !== "cancelled") ||
                  (step.key === "confirmed" && selected.status === "confirmed");
                const cancelled =
                  selected.status === "cancelled" && step.key === "confirmed";
                return (
                  <div key={step.key} className="flex items-center gap-2 text-sm">
                    <span className={cn(
                      "flex size-5 items-center justify-center rounded-full",
                      done      ? "bg-success text-success-foreground"     :
                      cancelled ? "bg-destructive text-destructive-foreground" :
                                  "border-2 border-muted-foreground/30 bg-card",
                    )}>
                      {done ? "✓" : cancelled ? <CloseIcon className="size-3" /> : ""}
                    </span>
                    <span className={cancelled ? "text-destructive" : ""}>{step.label}</span>
                  </div>
                );
              })}
              {selected.status === "cancelled" && (
                <div className="flex items-center gap-2 text-sm text-destructive">
                  <span className="flex size-5 items-center justify-center rounded-full bg-destructive text-destructive-foreground">
                    <CloseIcon className="size-3" />
                  </span>
                  Pesanan Dibatalkan
                </div>
              )}
            </div>

            <div className="flex flex-col gap-2">
              <span className="text-xs font-medium text-muted-foreground">Item</span>
              {selected.items.map((item, idx) => (
                // biome-ignore lint/suspicious/noArrayIndexKey: stable list
                <div key={idx} className="flex items-center justify-between text-sm">
                  <span>{item.quantity}x {item.menu?.name ?? `Item #${item.menu_item_id}`}</span>
                  <span className="font-medium">{formatRupiah(item.subtotal)}</span>
                </div>
              ))}
              <hr className="border-border" />
              <div className="flex items-center justify-between font-bold text-sm">
                <span>Total</span>
                <span>{formatRupiah(selected.total_price)}</span>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
