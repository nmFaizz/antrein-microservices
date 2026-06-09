"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Form } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { Switch } from "@/components/ui/switch";
import { Muted } from "@/components/ui/typography";
import { useCurrentUser } from "@/features/auth/hooks";
import {
  type QueueSettingsValues,
  queueSettingsSchema,
} from "@/features/queue/types";
import {
  useCreateSettings,
  useSettings,
  useUpdateSettings,
} from "@/features/queue-settings/queries";
import { formatDateTime } from "@/lib/format";

const emptyDefaults: QueueSettingsValues = {
  prefix: "A",
  grace_period_mins: 5,
  avg_serve_time_mins: 4,
  max_queue_per_day: 100,
  is_queue_open: true,
  open_time: "08:00",
  close_time: "21:00",
};

export default function SettingsPage() {
  const settingsQuery = useSettings();
  const currentUser = useCurrentUser();
  const createSettings = useCreateSettings();
  const updateSettings = useUpdateSettings();

  const settings = settingsQuery.data;
  const isConfigured = !!settings;

  const methods = useForm<QueueSettingsValues>({
    resolver: zodResolver(queueSettingsSchema),
    defaultValues: emptyDefaults,
  });

  const { reset } = methods;
  useEffect(() => {
    if (settings) {
      reset({
        prefix: settings.prefix,
        grace_period_mins: settings.grace_period_mins,
        avg_serve_time_mins: settings.avg_serve_time_mins,
        max_queue_per_day: settings.max_queue_per_day,
        is_queue_open: settings.is_queue_open,
        open_time: settings.open_time ?? "",
        close_time: settings.close_time ?? "",
      });
    }
  }, [settings, reset]);

  const mutation = isConfigured ? updateSettings : createSettings;
  const errorMessage =
    createSettings.error?.message ?? updateSettings.error?.message ?? null;
  const justSaved = createSettings.isSuccess || updateSettings.isSuccess;

  function handleSave(values: QueueSettingsValues) {
    const body = {
      ...values,
      open_time: values.open_time || null,
      close_time: values.close_time || null,
    };
    if (settings) {
      updateSettings.mutate({ id: settings.id, payload: body });
    } else {
      const adminId = currentUser.data?.id;
      if (!adminId) return;
      createSettings.mutate({ ...body, created_by: adminId });
    }
  }

  if (settingsQuery.isLoading) {
    return <p className="text-sm text-muted-foreground">Memuat pengaturan…</p>;
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Pengaturan Antrian"
        subtitle="Konfigurasi operasional antrian restoran"
      />

      {!isConfigured && (
        <div className="rounded-lg border border-primary/30 bg-accent px-4 py-3 text-sm">
          Antrian belum dikonfigurasi. Buat pengaturan terlebih dahulu agar
          pelanggan dapat mengambil nomor antrian.
        </div>
      )}

      <Form methods={methods} onSubmit={handleSave}>
        <Card>
          <CardHeader>
            <CardTitle>Umum</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2">
              <Input
                name="prefix"
                label="Prefix Nomor Antrian"
                placeholder="A"
                maxLength={3}
              />
              <Switch name="is_queue_open" label="Buka Antrian" />
              <Input name="open_time" label="Jam Buka" type="time" />
              <Input name="close_time" label="Jam Tutup" type="time" />
            </div>
            <Muted className="mt-2">Contoh prefix: A → A001, B → B001</Muted>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Waktu &amp; Kapasitas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-3">
              <Input
                name="grace_period_mins"
                label="Grace Period (menit)"
                type="number"
              />
              <Input
                name="avg_serve_time_mins"
                label="Rata-rata Waktu Layani (menit)"
                type="number"
              />
              <Input
                name="max_queue_per_day"
                label="Maks Antrian / Hari"
                type="number"
              />
            </div>
          </CardContent>
        </Card>

        {isConfigured && (
          <Card>
            <CardHeader>
              <CardTitle>Info</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
                <span>ID: {settings.id}</span>
                <span>Dibuat oleh: {settings.created_by}</span>
                <span>Dibuat: {formatDateTime(settings.created_at)}</span>
                <span>
                  Terakhir diperbarui: {formatDateTime(settings.updated_at)}
                </span>
              </div>
            </CardContent>
          </Card>
        )}

        {errorMessage && (
          <p className="text-sm text-destructive">{errorMessage}</p>
        )}
        {justSaved && !mutation.isPending && (
          <p className="text-sm text-success">Pengaturan tersimpan.</p>
        )}

        <Button type="submit" disabled={mutation.isPending}>
          {mutation.isPending
            ? "Menyimpan…"
            : isConfigured
              ? "Simpan Perubahan"
              : "Buat Pengaturan"}
        </Button>
      </Form>
    </div>
  );
}
