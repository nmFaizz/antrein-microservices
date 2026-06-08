"use client";

import type { ColumnDef } from "@tanstack/react-table";

import { Badge } from "@/components/ui/badge";
import { StatusBadge } from "@/components/ui/status-badge";
import { formatTime } from "@/lib/format";

import { formatQueueNumber, type Queue } from "./types";

/**
 * Queue table columns. `prefix` lets the number render as e.g. "A003";
 * `renderActions` injects per-row action buttons (call/serve/skip/…).
 */
export function getQueueColumns(
  prefix: string,
  renderActions?: (queue: Queue) => React.ReactNode,
): ColumnDef<Queue>[] {
  const columns: ColumnDef<Queue>[] = [
    {
      accessorKey: "queue_number",
      header: "No.",
      cell: ({ row }) => (
        <span className="font-semibold">
          {formatQueueNumber(prefix, row.original.queue_number)}
        </span>
      ),
    },
    {
      accessorKey: "customer_name",
      header: "Pelanggan",
      cell: ({ row }) => (
        <div className="flex flex-col">
          <span>{row.original.customer_name ?? "—"}</span>
          {row.original.is_requeued && (
            <span className="text-xs text-muted-foreground">
              Re-queue dari antrian sebelumnya
            </span>
          )}
        </div>
      ),
    },
    {
      accessorKey: "status_name",
      header: "Status",
      cell: ({ row }) => <StatusBadge name={row.original.status_name} />,
    },
    {
      accessorKey: "is_checked_in",
      header: "Check-in",
      cell: ({ row }) =>
        row.original.is_checked_in ? (
          <Badge variant="success">Sudah</Badge>
        ) : (
          <Badge variant="muted">Belum</Badge>
        ),
    },
    {
      accessorKey: "current_position",
      header: "Posisi",
      cell: ({ row }) =>
        row.original.status_name === "waiting" ||
        row.original.status_name === "re_queued"
          ? row.original.current_position
          : "—",
    },
    {
      accessorKey: "estimated_wait_minutes",
      header: "Estimasi",
      cell: ({ row }) =>
        row.original.estimated_wait_minutes > 0
          ? `${row.original.estimated_wait_minutes} mnt`
          : "—",
    },
    {
      accessorKey: "created_at",
      header: "Dibuat",
      cell: ({ row }) => formatTime(row.original.created_at),
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
