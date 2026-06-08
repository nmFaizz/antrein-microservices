"use client";

import { useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import {
  EditIcon,
  PlusIcon,
  TrashIcon,
} from "@/components/ui/icons";
import { PageHeader } from "@/components/ui/page-header";
import { SearchInput } from "@/components/ui/search-input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Form } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { formatRupiah } from "@/lib/format";
import { cn } from "@/lib/utils";
import { mockMenu } from "@/features/menu/mock";
import { menuSchema, type MenuCategory, type MenuItem, type MenuValues } from "@/features/menu/types";

const categoryOpts = [
  { label: "Makanan", value: "makanan" },
  { label: "Minuman", value: "minuman" },
  { label: "Camilan", value: "snacks" },
];

const categories = [
  { label: "Semua", value: "" },
  ...categoryOpts,
];

type FormMode = "add" | "edit";

export default function AdminMenuPage() {
  const [items, setItems] = useState<MenuItem[]>(mockMenu);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [formMode, setFormMode] = useState<FormMode | null>(null);
  const [editing, setEditing] = useState<MenuItem | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<MenuItem | null>(null);

  const methods = useForm<MenuValues>({
    resolver: zodResolver(menuSchema),
    defaultValues: { name: "", description: "", price: 0, category: "makanan", is_available: true },
  });

  const activeItems = useMemo(() => items.filter((i) => !i.is_deleted), [items]);

  const filtered = useMemo(() => {
    return activeItems.filter((item) => {
      const matchSearch = item.name.toLowerCase().includes(search.toLowerCase());
      const matchCategory = !category || item.category === category;
      return matchSearch && matchCategory;
    });
  }, [activeItems, search, category]);

  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const item of activeItems) {
      counts[item.category] = (counts[item.category] || 0) + 1;
    }
    return counts;
  }, [activeItems]);

  function openAdd() {
    setFormMode("add");
    setEditing(null);
    methods.reset({ name: "", description: "", price: 0, category: "makanan", is_available: true });
  }

  function openEdit(item: MenuItem) {
    setFormMode("edit");
    setEditing(item);
    methods.reset({
      name: item.name,
      description: item.description ?? "",
      price: item.price,
      category: item.category,
      is_available: item.is_available,
    });
  }

  function save(data: MenuValues) {
    const price = Number(data.price);
    if (formMode === "add") {
      const newItem: MenuItem = {
        id: `m${Date.now()}`,
        name: data.name,
        description: data.description || null,
        price,
        category: data.category as MenuCategory,
        is_available: data.is_available,
        is_deleted: false,
        created_at: new Date().toISOString(),
        updated_at: null,
      };
      setItems((prev) => [...prev, newItem]);
    } else if (editing) {
      setItems((prev) =>
        prev.map((item) =>
          item.id === editing.id
            ? { ...item, name: data.name, description: data.description || null, price, category: data.category as MenuCategory, is_available: data.is_available, updated_at: new Date().toISOString() }
            : item,
        ),
      );
    }
    setFormMode(null);
    setEditing(null);
  }

  function toggleAvailability(id: string) {
    setItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, is_available: !item.is_available } : item,
      ),
    );
  }

  function confirmDelete() {
    if (!deleteTarget) return;
    setItems((prev) =>
      prev.map((item) =>
        item.id === deleteTarget.id ? { ...item, is_deleted: true } : item,
      ),
    );
    setDeleteTarget(null);
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Menu Management"
        subtitle={`${activeItems.length} menu aktif`}
        actions={
          <Button onClick={openAdd}>
            <PlusIcon className="size-4" /> Tambah Menu
          </Button>
        }
      />

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <SearchInput
          className="sm:max-w-xs"
          placeholder="Cari menu…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="flex gap-2 overflow-x-auto">
          {categories.map((cat) => (
            <button
              key={cat.value}
              type="button"
              onClick={() => setCategory(cat.value)}
              className={cn(
                "shrink-0 rounded-full px-3 py-1.5 text-xs font-medium transition",
                category === cat.value
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-accent hover:text-foreground",
              )}
            >
              {cat.label}
              {cat.value && (
                <span className="ml-1.5 opacity-60">
                  {categoryCounts[cat.value] ?? 0}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead className="border-b border-border bg-muted">
            <tr>
              {["Nama", "Kategori", "Harga", "Status", "Aksi"].map((h) => (
                <th key={h} className="px-4 py-2.5 text-left font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((item) => (
              <tr key={item.id} className="border-b border-border last:border-0">
                <td className="px-4 py-2.5">
                  <div className="flex flex-col">
                    <span className="font-medium">{item.name}</span>
                    {item.description && (
                      <span className="line-clamp-1 text-xs text-muted-foreground">{item.description}</span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-2.5">
                  <Badge variant={item.category === "makanan" ? "info" : item.category === "minuman" ? "default" : "warning"}>
                    {item.category === "snacks" ? "Camilan" : item.category}
                  </Badge>
                </td>
                <td className="px-4 py-2.5 font-medium">{formatRupiah(item.price)}</td>
                <td className="px-4 py-2.5">
                  <button
                    type="button"
                    onClick={() => toggleAvailability(item.id)}
                    className={cn(
                      "rounded-full px-2.5 py-0.5 text-xs font-medium transition",
                      item.is_available
                        ? "bg-green-100 text-green-700 hover:bg-green-200"
                        : "bg-muted text-muted-foreground hover:bg-accent",
                    )}
                  >
                    {item.is_available ? "Tersedia" : "Habis"}
                  </button>
                </td>
                <td className="px-4 py-2.5">
                  <div className="flex gap-1">
                    <button
                      type="button"
                      onClick={() => openEdit(item)}
                      className="flex size-8 items-center justify-center rounded-md text-muted-foreground transition hover:bg-accent hover:text-foreground"
                      aria-label="Edit"
                    >
                      <EditIcon className="size-4" />
                    </button>
                    <button
                      type="button"
                      onClick={() => setDeleteTarget(item)}
                      className="flex size-8 items-center justify-center rounded-md text-muted-foreground transition hover:bg-destructive/10 hover:text-destructive"
                      aria-label="Hapus"
                    >
                      <TrashIcon className="size-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {(formMode === "add" || formMode === "edit") && (
        <Form methods={methods} onSubmit={save}>
          <Card className="border-primary/30">
            <CardHeader>
              <CardTitle>{formMode === "add" ? "Tambah Menu Baru" : "Edit Menu"}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-4">
                <Input name="name" label="Nama" placeholder="Nama menu" />
                <Textarea name="description" label="Deskripsi" placeholder="Deskripsi menu (opsional)" />
                <div className="grid grid-cols-2 gap-3">
                  <Input name="price" label="Harga (Rp)" type="number" placeholder="25000" />
                  <Select name="category" label="Kategori" options={categoryOpts} />
                </div>
                <Checkbox name="is_available" label="Tersedia" />
                <div className="flex justify-end gap-2">
                  <Button variant="ghost" type="button" onClick={() => setFormMode(null)}>Batal</Button>
                  <Button type="submit">Simpan</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </Form>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={confirmDelete}
        title="Hapus Menu"
        description={`Yakin ingin menghapus "${deleteTarget?.name}"?`}
        confirmLabel="Ya, Hapus"
        cancelLabel="Batal"
        confirmVariant="destructive"
      />
    </div>
  );
}
