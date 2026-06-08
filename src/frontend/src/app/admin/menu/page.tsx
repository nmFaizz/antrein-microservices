"use client";

import { useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { EditIcon, PlusIcon, TrashIcon } from "@/components/ui/icons";
import { PageHeader } from "@/components/ui/page-header";
import { SearchInput } from "@/components/ui/search-input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Form } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Muted } from "@/components/ui/typography";
import { formatRupiah } from "@/lib/format";
import { cn } from "@/lib/utils";
import {
  MENU_CATEGORIES,
  menuSchema,
  type MenuItem,
  type MenuValues,
} from "@/features/menu/types";
import {
  useMenuItems,
  useCreateMenu,
  useUpdateMenu,
  useUpdateMenuAvailability,
  useDeleteMenu,
} from "@/features/menu/queries";

const categoryOpts = MENU_CATEGORIES;
const allCategories = [{ label: "Semua", value: "" }, ...categoryOpts];

type FormMode = "add" | "edit";

export default function AdminMenuPage() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [formMode, setFormMode] = useState<FormMode | null>(null);
  const [editing, setEditing] = useState<MenuItem | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<MenuItem | null>(null);
  const [mutationError, setMutationError] = useState<string | null>(null);

  const { data: items = [], isLoading, isError } = useMenuItems();
  const createMenu = useCreateMenu();
  const updateMenu = useUpdateMenu();
  const updateAvailability = useUpdateMenuAvailability();
  const deleteMenu = useDeleteMenu();

  const methods = useForm<MenuValues>({
    resolver: zodResolver(menuSchema),
    defaultValues: {
      name: "",
      description: "",
      price: 0,
      category: "makanan",
      is_available: true,
    },
  });

  const activeItems = useMemo(() => items.filter((i) => !i.is_deleted), [items]);

  const filtered = useMemo(() => {
    return activeItems.filter((item) => {
      const matchSearch = item.name
        .toLowerCase()
        .includes(search.toLowerCase());
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
    setMutationError(null);
    methods.reset({
      name: "",
      description: "",
      price: 0,
      category: "makanan",
      is_available: true,
    });
  }

  function openEdit(item: MenuItem) {
    setFormMode("edit");
    setEditing(item);
    setMutationError(null);
    methods.reset({
      name: item.name,
      description: item.description ?? "",
      price: item.price,
      category: item.category,
      is_available: item.is_available,
    });
  }

  async function save(data: MenuValues) {
    setMutationError(null);
    try {
      if (formMode === "add") {
        await createMenu.mutateAsync(data);
      } else if (editing) {
        await updateMenu.mutateAsync({ id: editing.id, data });
      }
      setFormMode(null);
      setEditing(null);
    } catch (err) {
      setMutationError(
        err instanceof Error ? err.message : "Gagal menyimpan menu",
      );
    }
  }

  function toggleAvailability(item: MenuItem) {
    updateAvailability.mutate({ id: item.id, isAvailable: !item.is_available });
  }

  async function confirmDelete() {
    if (!deleteTarget) return;
    try {
      await deleteMenu.mutateAsync(deleteTarget.id);
    } catch {
      // list stays unchanged if request fails
    }
    setDeleteTarget(null);
  }

  const isSaving = createMenu.isPending || updateMenu.isPending;

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
          {allCategories.map((cat) => (
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
                <th key={h} className="px-4 py-2.5 text-left font-medium">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading &&
              Array.from({ length: 4 }).map((_, i) => (
                // biome-ignore lint/suspicious/noArrayIndexKey: skeleton
                <tr key={i} className="border-b border-border">
                  {Array.from({ length: 5 }).map((__, j) => (
                    // biome-ignore lint/suspicious/noArrayIndexKey: skeleton
                    <td key={j} className="px-4 py-3">
                      <div className="h-4 animate-pulse rounded bg-muted" />
                    </td>
                  ))}
                </tr>
              ))}

            {isError && (
              <tr>
                <td colSpan={5} className="px-4 py-10 text-center">
                  <Muted>Gagal memuat menu. Coba lagi nanti.</Muted>
                </td>
              </tr>
            )}

            {!isLoading &&
              !isError &&
              filtered.map((item) => (
                <tr
                  key={item.id}
                  className="border-b border-border last:border-0"
                >
                  <td className="px-4 py-2.5">
                    <div className="flex flex-col">
                      <span className="font-medium">{item.name}</span>
                      {item.description && (
                        <span className="line-clamp-1 text-xs text-muted-foreground">
                          {item.description}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-2.5">
                    <Badge
                      variant={item.category === "makanan" ? "info" : "default"}
                    >
                      {item.category}
                    </Badge>
                  </td>
                  <td className="px-4 py-2.5 font-medium">
                    {formatRupiah(item.price)}
                  </td>
                  <td className="px-4 py-2.5">
                    <button
                      type="button"
                      onClick={() => toggleAvailability(item)}
                      disabled={updateAvailability.isPending}
                      className={cn(
                        "rounded-full px-2.5 py-0.5 text-xs font-medium transition disabled:opacity-50",
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

            {!isLoading && !isError && filtered.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-10 text-center">
                  <Muted>Menu tidak ditemukan.</Muted>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {(formMode === "add" || formMode === "edit") && (
        <Form methods={methods} onSubmit={save}>
          <Card className="border-primary/30">
            <CardHeader>
              <CardTitle>
                {formMode === "add" ? "Tambah Menu Baru" : "Edit Menu"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-4">
                <Input name="name" label="Nama" placeholder="Nama menu" />
                <Textarea
                  name="description"
                  label="Deskripsi"
                  placeholder="Deskripsi menu (opsional)"
                />
                <div className="grid grid-cols-2 gap-3">
                  <Input
                    name="price"
                    label="Harga (Rp)"
                    type="number"
                    placeholder="25000"
                  />
                  <Select
                    name="category"
                    label="Kategori"
                    options={categoryOpts}
                  />
                </div>
                <Checkbox name="is_available" label="Tersedia" />
                {mutationError && (
                  <p className="text-sm text-destructive">{mutationError}</p>
                )}
                <div className="flex justify-end gap-2">
                  <Button
                    variant="ghost"
                    type="button"
                    onClick={() => setFormMode(null)}
                    disabled={isSaving}
                  >
                    Batal
                  </Button>
                  <Button type="submit" disabled={isSaving}>
                    {isSaving ? "Menyimpan…" : "Simpan"}
                  </Button>
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
        confirmLabel={deleteMenu.isPending ? "Menghapus…" : "Ya, Hapus"}
        cancelLabel="Batal"
        confirmVariant="destructive"
      />
    </div>
  );
}
