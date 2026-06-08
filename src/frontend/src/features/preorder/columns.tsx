"use client";

import type { ColumnDef } from "@tanstack/react-table";

import { Badge, type BadgeVariant } from "@/components/ui/badge";
import { formatDateTime, formatRupiah } from "@/lib/format";

import type { Preorder, PreorderStatus } from "./types";

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

/** Preorder table columns. `renderActions` injects a per-row detail button. */
export function getPreorderColumns(
  renderActions?: (preorder: Preorder) => React.ReactNode,
): ColumnDef<Preorder>[] {
  const columns: ColumnDef<Preorder>[] = [
    {
      accessorKey: "id",
      header: "ID",
      cell: ({ row }) => (
        <span className="font-mono text-xs uppercase">
          #{row.original.id}
        </span>
      ),
    },
    {
      accessorKey: "customer_name",
      header: "Pelanggan",
      cell: ({ row }) => row.original.customer_name ?? "—",
    },
    {
      id: "items",
      header: "Item",
      cell: ({ row }) => `${row.original.items.length} item`,
    },
    {
      accessorKey: "total_price",
      header: "Total",
      cell: ({ row }) => (
        <span className="font-medium">
          {formatRupiah(row.original.total_price)}
        </span>
      ),
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => (
        <Badge variant={statusVariant[row.original.status]}>
          {statusLabel[row.original.status]}
        </Badge>
      ),
    },
    {
      id: "queue",
      header: "Antrian",
      cell: ({ row }) =>
        row.original.queue ? (
          <span className="font-semibold">
            {row.original.queue.queue_number}
          </span>
        ) : (
          "—"
        ),
    },
    {
      accessorKey: "created_at",
      header: "Waktu",
      cell: ({ row }) => formatDateTime(row.original.created_at),
    },
  ];

  if (renderActions) {
    columns.push({
      id: "actions",
      header: () => <span className="sr-only">Aksi</span>,
      cell: ({ row }) => (
        <div className="flex justify-end">{renderActions(row.original)}</div>
      ),
    });
  }

  return columns;
}

export { statusLabel as preorderStatusLabel };
