"use client";

import type { ColumnDef } from "@tanstack/react-table";

import { Badge } from "@/components/ui/badge";
import { formatRupiah } from "@/lib/format";

import type { MenuItem } from "./types";

/** Menu table columns. `renderActions` injects per-row edit/delete buttons. */
export function getMenuColumns(
  renderActions?: (menu: MenuItem) => React.ReactNode,
): ColumnDef<MenuItem>[] {
  const columns: ColumnDef<MenuItem>[] = [
    {
      accessorKey: "name",
      header: "Nama",
      cell: ({ row }) => (
        <div className="flex flex-col">
          <span className="font-medium">{row.original.name}</span>
          {row.original.description && (
            <span className="line-clamp-1 text-xs text-muted-foreground">
              {row.original.description}
            </span>
          )}
        </div>
      ),
    },
    {
      accessorKey: "category",
      header: "Kategori",
      cell: ({ row }) => (
        <Badge
          variant={row.original.category === "makanan" ? "info" : "default"}
        >
          {row.original.category}
        </Badge>
      ),
    },
    {
      accessorKey: "price",
      header: "Harga",
      cell: ({ row }) => formatRupiah(row.original.price),
    },
    {
      accessorKey: "is_available",
      header: "Tersedia",
      cell: ({ row }) =>
        row.original.is_available ? (
          <Badge variant="success">Tersedia</Badge>
        ) : (
          <Badge variant="muted">Habis</Badge>
        ),
    },
  ];

  if (renderActions) {
    columns.push({
      id: "actions",
      header: () => <span className="sr-only">Aksi</span>,
      cell: ({ row }) => (
        <div className="flex justify-end gap-1">
          {renderActions(row.original)}
        </div>
      ),
    });
  }

  return columns;
}
