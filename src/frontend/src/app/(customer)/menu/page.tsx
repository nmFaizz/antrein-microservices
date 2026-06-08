"use client";

import { useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { PlusIcon } from "@/components/ui/icons";
import { SearchInput } from "@/components/ui/search-input";
import { useCart } from "@/components/ui/cart-provider";
import { Button } from "@/components/ui/button";
import { H2, Muted } from "@/components/ui/typography";
import { formatRupiah } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { MenuItem } from "@/features/menu/types";
import { mockMenu } from "@/features/menu/mock";

const categories = [
  { label: "Semua", value: "" },
  { label: "Makanan", value: "makanan" },
  { label: "Minuman", value: "minuman" },
  { label: "Camilan", value: "snacks" },
];

export default function MenuPage() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const { add, itemCount, total } = useCart();

  const filtered = useMemo(() => {
    return mockMenu.filter((item) => {
      const matchSearch = item.name
        .toLowerCase()
        .includes(search.toLowerCase());
      const matchCategory = !category || item.category === category;
      return matchSearch && matchCategory && !item.is_deleted;
    });
  }, [search, category]);

  return (
    <div className="flex flex-col gap-4 px-4 py-5 pb-24">
      <H2>Menu</H2>

      <SearchInput
        placeholder="Cari menu…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      <div className="flex gap-2 overflow-x-auto pb-1">
        {categories.map((cat) => (
          <button
            key={cat.value}
            type="button"
            onClick={() => setCategory(cat.value)}
            className={cn(
              "shrink-0 rounded-full px-4 py-1.5 text-sm font-medium transition",
              category === cat.value
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-accent hover:text-foreground",
            )}
          >
            {cat.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-3">
        {filtered.map((item) => (
          <MenuCard key={item.id} item={item} onAdd={add} />
        ))}
        {filtered.length === 0 && (
          <Muted className="col-span-full py-12 text-center">
            Menu tidak ditemukan.
          </Muted>
        )}
      </div>

      {itemCount > 0 && (
        <div className="fixed bottom-16 left-0 right-0 z-20 border-t border-border bg-card px-4 py-3 shadow-lg">
          <div className="mx-auto flex max-w-lg items-center justify-between">
            <div className="flex flex-col">
              <span className="text-sm font-medium">{itemCount} item</span>
              <span className="text-lg font-bold">{formatRupiah(total)}</span>
            </div>
            <a href="/preorder">
              <Button size="lg">Pesan Sekarang</Button>
            </a>
          </div>
        </div>
      )}
    </div>
  );
}

function MenuCard({
  item,
  onAdd,
}: {
  item: MenuItem;
  onAdd: (item: MenuItem) => void;
}) {
  return (
    <div className="flex flex-col overflow-hidden rounded-lg border border-border bg-card shadow-sm">
      <div className="aspect-[4/3] bg-muted" />
      <div className="flex flex-1 flex-col gap-1.5 p-3">
        <span className="font-semibold leading-tight">{item.name}</span>
        {item.description && (
          <span className="line-clamp-1 text-xs text-muted-foreground">
            {item.description}
          </span>
        )}
        <span className="mt-auto font-bold text-primary-700">
          {formatRupiah(item.price)}
        </span>
        <div className="flex items-center justify-between">
          {item.is_available ? (
            <Badge variant="success">Tersedia</Badge>
          ) : (
            <Badge variant="muted">Habis</Badge>
          )}
          <button
            type="button"
            disabled={!item.is_available}
            onClick={() => onAdd(item)}
            className={cn(
              "flex size-8 items-center justify-center rounded-full transition",
              item.is_available
                ? "bg-primary text-primary-foreground hover:bg-primary-500"
                : "bg-muted text-muted-foreground",
            )}
            aria-label={`Tambah ${item.name}`}
          >
            <PlusIcon className="size-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
