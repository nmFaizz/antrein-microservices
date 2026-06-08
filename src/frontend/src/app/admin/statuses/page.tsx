"use client";

import { useState } from "react";
import { useForm, useFormContext } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import {
  EditIcon,
  PlusIcon,
  TrashIcon,
} from "@/components/ui/icons";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Field } from "@/components/ui/field";
import { Form } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { mockStatuses } from "@/features/queue/mock";
import { queueStatusSchema, type QueueStatus, type QueueStatusValues } from "@/features/queue/types";

const presetColors = [
  "#9CA3AF", "#3B82F6", "#10B981", "#F97316",
  "#8B5CF6", "#EF4444", "#FACC15", "#EC4899",
  "#06B6D4", "#84CC16",
];

type FormMode = "add" | "edit";

function ColorPicker({ name }: { name: string }) {
  const { register, watch, setValue } = useFormContext();
  const currentColor = watch(name);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <span
          className="size-9 shrink-0 rounded-md border"
          style={{ backgroundColor: currentColor || "#ccc" }}
        />
        <input
          className="h-10 flex-1 rounded-md border border-input bg-background px-3 font-mono text-sm outline-none transition focus:border-ring focus:ring-2 focus:ring-ring/30"
          placeholder="#9CA3AF"
          {...register(name)}
        />
      </div>
      <div className="flex flex-wrap gap-1.5">
        {presetColors.map((c) => (
          <button
            key={c}
            type="button"
            onClick={() => setValue(name, c, { shouldValidate: true })}
            className={cn(
              "size-7 rounded-full border-2 transition",
              currentColor === c ? "border-foreground scale-110" : "border-transparent",
            )}
            style={{ backgroundColor: c }}
            aria-label={c}
          />
        ))}
      </div>
    </div>
  );
}

export default function StatusesPage() {
  const [statuses, setStatuses] = useState<QueueStatus[]>(mockStatuses);
  const [formMode, setFormMode] = useState<FormMode | null>(null);
  const [editing, setEditing] = useState<QueueStatus | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<QueueStatus | null>(null);

  const methods = useForm<QueueStatusValues>({
    resolver: zodResolver(queueStatusSchema),
    defaultValues: { name: "", color: "#9CA3AF" },
  });

  function openAdd() {
    setFormMode("add");
    setEditing(null);
    methods.reset({ name: "", color: "#9CA3AF" });
  }

  function openEdit(status: QueueStatus) {
    setFormMode("edit");
    setEditing(status);
    methods.reset({ name: status.name, color: status.color ?? "#9CA3AF" });
  }

  function save(data: QueueStatusValues) {
    const name = data.name.trim().toLowerCase().replace(/\s+/g, "_");
    if (formMode === "add") {
      const newStatus: QueueStatus = {
        id: `st-${Date.now()}`,
        name,
        color: data.color,
      };
      setStatuses((prev) => [...prev, newStatus]);
    } else if (editing) {
      setStatuses((prev) =>
        prev.map((s) =>
          s.id === editing.id ? { ...s, name, color: data.color } : s,
        ),
      );
    }
    setFormMode(null);
    setEditing(null);
  }

  function confirmDelete() {
    if (!deleteTarget) return;
    setStatuses((prev) => prev.filter((s) => s.id !== deleteTarget.id));
    setDeleteTarget(null);
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Status Antrian"
        subtitle={`${statuses.length} status terdaftar`}
        actions={
          <Button onClick={openAdd}>
            <PlusIcon className="size-4" /> Tambah Status
          </Button>
        }
      />

      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead className="border-b border-border bg-muted">
            <tr>
              {["Warna", "Nama Status", "ID", "Aksi"].map((h) => (
                <th key={h} className="px-4 py-2.5 text-left font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {statuses.map((status) => (
              <tr key={status.id} className="border-b border-border last:border-0">
                <td className="px-4 py-2.5">
                  <div className="flex items-center gap-2">
                    <span
                      className="size-6 rounded-full border"
                      style={{ backgroundColor: status.color ?? "#ccc" }}
                    />
                    <code className="text-xs text-muted-foreground">{status.color}</code>
                  </div>
                </td>
                <td className="px-4 py-2.5 font-medium capitalize">
                  {status.name.replace(/_/g, " ")}
                </td>
                <td className="px-4 py-2.5 font-mono text-xs text-muted-foreground">
                  {status.id}
                </td>
                <td className="px-4 py-2.5">
                  <div className="flex gap-1">
                    <button
                      type="button"
                      onClick={() => openEdit(status)}
                      className="flex size-8 items-center justify-center rounded-md text-muted-foreground transition hover:bg-accent hover:text-foreground"
                      aria-label="Edit"
                    >
                      <EditIcon className="size-4" />
                    </button>
                    <button
                      type="button"
                      onClick={() => setDeleteTarget(status)}
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
          <div className="rounded-lg border border-primary/30 bg-card p-5">
            <h3 className="mb-4 text-base font-semibold">
              {formMode === "add" ? "Tambah Status Baru" : "Edit Status"}
            </h3>
            <div className="flex flex-col gap-4">
              <Input name="name" label="Nama Status" placeholder="contoh: preparing" />
              <Field name="color" label="Warna">
                <ColorPicker name="color" />
              </Field>
              <p className="text-xs text-muted-foreground">
                Nama akan otomatis diubah: huruf kecil, spasi diganti underscore
              </p>
              <div className="flex justify-end gap-2">
                <Button variant="ghost" type="button" onClick={() => setFormMode(null)}>Batal</Button>
                <Button type="submit">Simpan</Button>
              </div>
            </div>
          </div>
        </Form>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={confirmDelete}
        title="Hapus Status"
        description={
          deleteTarget
            ? `Yakin ingin menghapus status "${deleteTarget.name.replace(/_/g, " ")}"? Status yang sedang digunakan pada antrian aktif mungkin akan bermasalah.`
            : ""
        }
        confirmLabel="Ya, Hapus"
        cancelLabel="Batal"
        confirmVariant="destructive"
      />
    </div>
  );
}
