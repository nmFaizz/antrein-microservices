"use client";

import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { ChevronRightIcon } from "@/components/ui/icons";
import { Muted, Small } from "@/components/ui/typography";

const mockQueue = {
  queueNumber: "A005",
  position: 3,
  estimatedWait: 12,
  status: "waiting" as const,
  nowServing: "A003",
};

const queueStatusBadge: Record<string, { label: string; variant: "warning" | "success" | "info" }> = {
  waiting: { label: "Menunggu", variant: "warning" },
  called: { label: "Dipanggil!", variant: "success" },
  serving: { label: "Sedang Dilayani", variant: "info" },
};

export default function QueuePage() {
  const q = queueStatusBadge[mockQueue.status];

  return (
    <div className="flex min-h-[80vh] flex-col items-center justify-center gap-6 px-6 text-center">
      <Muted>Nomor Antrian Kamu</Muted>
      <span className="text-8xl font-bold tracking-tighter text-primary-600">
        {mockQueue.queueNumber}
      </span>
      <Badge variant={q.variant} className="text-base px-5 py-1">
        {q.label}
      </Badge>

      <div className="mt-2 grid w-full max-w-xs grid-cols-2 gap-3">
        <div className="rounded-lg bg-muted p-4">
          <span className="text-xs text-muted-foreground">Posisi</span>
          <p className="text-xl font-bold">{mockQueue.position} orang</p>
        </div>
        <div className="rounded-lg bg-muted p-4">
          <span className="text-xs text-muted-foreground">Estimasi</span>
          <p className="text-xl font-bold">~{mockQueue.estimatedWait} menit</p>
        </div>
      </div>

      <Card className="w-full max-w-xs">
        <CardContent className="flex items-center justify-between py-3">
          <div className="flex flex-col text-left">
              <Small className="text-muted-foreground">Sekarang dipanggil</Small>
            <span className="text-lg font-bold">{mockQueue.nowServing}</span>
          </div>
          <Badge variant="info">{mockQueue.nowServing}</Badge>
        </CardContent>
      </Card>

      <Link
        href="/preorder"
        className="inline-flex items-center gap-1 text-sm font-medium text-primary-600 hover:underline"
      >
        Lihat pesanan kamu <ChevronRightIcon className="size-4" />
      </Link>

      <Small className="text-muted-foreground">
        Halaman diperbarui secara otomatis
      </Small>
    </div>
  );
}
