"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ButtonLink } from "@/components/ui/button-link";
import { Card, CardContent } from "@/components/ui/card";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { EmptyState } from "@/components/ui/empty-state";
import { ChevronRightIcon, TicketIcon } from "@/components/ui/icons";
import { StatusBadge } from "@/components/ui/status-badge";
import { Muted, Small } from "@/components/ui/typography";
import { useMyPreorders } from "@/features/preorder/queries";
import { useCancelQueue, useCheckIn, useQueue } from "@/features/queue/queries";
import { STATUS_COLORS } from "@/features/queue/types";

const ACTIVE_QUEUE_STATUSES = ["waiting", "called", "re_queued"];

export default function QueuePage() {
  const preordersQuery = useMyPreorders();
  const [showCancel, setShowCancel] = useState(false);

  // The customer's queue id comes from their most recent preorder that still
  // has an active queue snapshot (queue creation is backend-driven on preorder).
  const activeQueueId = useMemo(() => {
    const preorders = [...(preordersQuery.data ?? [])].sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
    );
    const withQueue = preorders.find(
      (p) =>
        p.queue &&
        ACTIVE_QUEUE_STATUSES.includes(p.queue.status) &&
        p.status !== "cancelled",
    );
    return withQueue?.queue?.id;
  }, [preordersQuery.data]);

  const queueQuery = useQueue(activeQueueId, { refetchInterval: 15_000 });
  const checkIn = useCheckIn();
  const cancelQueue = useCancelQueue();

  const queue = queueQuery.data;

  if (preordersQuery.isLoading || (activeQueueId && queueQuery.isLoading)) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Muted>Memuat antrian…</Muted>
      </div>
    );
  }

  if (!queue || !ACTIVE_QUEUE_STATUSES.includes(queue.status_name)) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center px-6">
        <EmptyState
          icon={<TicketIcon className="size-6" />}
          title="Belum ada antrian aktif"
          description="Buat pre-order untuk mendapatkan nomor antrian."
          action={<ButtonLink href="/menu">Lihat Menu</ButtonLink>}
        />
      </div>
    );
  }

  const isCalled = queue.status_name === "called";
  const canCheckIn = !queue.is_checked_in && queue.status_name !== "cancelled";
  const canCancel = queue.status_name === "waiting";

  return (
    <div className="flex min-h-[80vh] flex-col items-center justify-center gap-6 px-6 text-center">
      <Muted>Nomor Antrian Kamu</Muted>
      <span className="text-8xl font-bold tracking-tighter text-primary-600">
        {queue.queue_number}
      </span>
      <StatusBadge
        name={queue.status_name}
        color={STATUS_COLORS[queue.status_name]}
        className="px-5 py-1 text-base"
      />

      {isCalled && (
        <p className="font-medium text-success">
          Giliranmu! Silakan menuju counter.
        </p>
      )}

      <div className="mt-2 grid w-full max-w-xs grid-cols-2 gap-3">
        <div className="rounded-lg bg-muted p-4">
          <span className="text-xs text-muted-foreground">Posisi</span>
          <p className="text-xl font-bold">
            {queue.current_position > 0
              ? `${queue.current_position} orang`
              : "—"}
          </p>
        </div>
        <div className="rounded-lg bg-muted p-4">
          <span className="text-xs text-muted-foreground">Estimasi</span>
          <p className="text-xl font-bold">
            {queue.estimated_wait_minutes > 0
              ? `~${queue.estimated_wait_minutes} menit`
              : "—"}
          </p>
        </div>
      </div>

      <Card className="w-full max-w-xs">
        <CardContent className="flex items-center justify-between py-3">
          <div className="flex flex-col text-left">
            <Small className="text-muted-foreground">Check-in</Small>
            <span className="text-lg font-bold">
              {queue.is_checked_in ? "Sudah" : "Belum"}
            </span>
          </div>
          <Badge variant={queue.is_checked_in ? "success" : "muted"}>
            {queue.is_checked_in ? "Hadir" : "Belum hadir"}
          </Badge>
        </CardContent>
      </Card>

      <div className="flex w-full max-w-xs flex-col gap-2">
        {canCheckIn && (
          <Button
            onClick={() => checkIn.mutate(queue.id)}
            disabled={checkIn.isPending}
          >
            {checkIn.isPending ? "Memproses…" : "Check-in Sekarang"}
          </Button>
        )}
        {canCancel && (
          <Button
            variant="outline"
            onClick={() => setShowCancel(true)}
            disabled={cancelQueue.isPending}
          >
            Batalkan Antrian
          </Button>
        )}
      </div>

      {(checkIn.error || cancelQueue.error) && (
        <p className="text-sm text-destructive">
          {checkIn.error?.message ?? cancelQueue.error?.message}
        </p>
      )}

      <Link
        href="/preorder/history"
        className="inline-flex items-center gap-1 text-sm font-medium text-primary-600 hover:underline"
      >
        Lihat pesanan kamu <ChevronRightIcon className="size-4" />
      </Link>

      <Small className="text-muted-foreground">
        Halaman diperbarui otomatis setiap 15 detik
      </Small>

      <ConfirmDialog
        open={showCancel}
        onClose={() => setShowCancel(false)}
        onConfirm={() => cancelQueue.mutate(queue.id)}
        title="Batalkan antrian?"
        description="Kamu hanya bisa membatalkan sebelum dipanggil. Tindakan ini tidak bisa dibatalkan."
        confirmLabel="Ya, batalkan"
        cancelLabel="Kembali"
        confirmVariant="destructive"
      />
    </div>
  );
}
