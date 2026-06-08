"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Form } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Muted } from "@/components/ui/typography";
import { formatDateTime } from "@/lib/format";
import { mockSettings } from "@/features/queue/mock";
import { queueSettingsSchema, type QueueSettingsValues } from "@/features/queue/types";

export default function SettingsPage() {
  const [dirty, setDirty] = useState(false);

  const methods = useForm<QueueSettingsValues>({
    resolver: zodResolver(queueSettingsSchema),
    defaultValues: {
      prefix: mockSettings.prefix,
      grace_period_mins: mockSettings.grace_period_mins,
      avg_serve_time_mins: mockSettings.avg_serve_time_mins,
      max_queue_per_day: mockSettings.max_queue_per_day,
      is_queue_open: mockSettings.is_queue_open,
      open_time: mockSettings.open_time ?? "",
      close_time: mockSettings.close_time ?? "",
    },
  });

  function handleSave() {
    setDirty(false);
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Pengaturan Antrian"
        subtitle="Konfigurasi operasional antrian restoran"
      />

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
              <Checkbox name="is_queue_open" label="Buka Antrian" />
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

        <Card>
          <CardHeader>
            <CardTitle>Info</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
              <span>ID: {mockSettings.id}</span>
              <span>Dibuat oleh: {mockSettings.created_by}</span>
              <span>Dibuat: {formatDateTime(mockSettings.created_at)}</span>
              <span>Terakhir diperbarui: {formatDateTime(mockSettings.updated_at)}</span>
            </div>
          </CardContent>
        </Card>

        <Button type="submit">Simpan Pengaturan</Button>
      </Form>
    </div>
  );
}
