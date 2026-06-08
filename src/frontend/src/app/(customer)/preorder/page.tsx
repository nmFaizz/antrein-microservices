"use client";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { CheckIcon, ClockIcon, CloseIcon } from "@/components/ui/icons";
import { useCart } from "@/components/ui/cart-provider";
import { Button } from "@/components/ui/button";
import { H2, Muted } from "@/components/ui/typography";
import { formatRupiah } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { PreorderStatus } from "@/features/preorder/types";

const mockQueue = {
  queueNumber: "A005",
  position: 3,
  estimatedWait: 12,
  status: "waiting" as const,
};

const mockOrder = {
  id: "ORD-2024-0042",
  status: "pending" as PreorderStatus,
  notes: "Tidak pakai pedas",
  createdAt: "10:32",
  items: [{ name: "Nasi Goreng Spesial", quantity: 2, subtotal: 50000 }],
  totalPrice: 50000,
};

const queueLabel: Record<string, { label: string; variant: "warning" | "success" | "info" }> = {
  waiting: { label: "Menunggu", variant: "warning" },
  called: { label: "Dipanggil", variant: "success" },
  serving: { label: "Dilayani", variant: "info" },
};

const statusLabel: Record<PreorderStatus, string> = {
  pending: "Menunggu Konfirmasi",
  confirmed: "Dikonfirmasi",
  cancelled: "Dibatalkan",
};

export default function PreorderPage() {
  const { total } = useCart();

  function getSteps(status: PreorderStatus) {
    if (status === "cancelled") {
      return [
        { key: "pending", label: "Pesanan Diterima", done: true, cancelled: false },
        { key: "cancelled", label: "Pesanan Dibatalkan", done: false, cancelled: true },
      ];
    }
    return [
      { key: "pending", label: "Pesanan Diterima", done: status !== "pending", cancelled: false },
      { key: "confirmed", label: "Pesanan Dikonfirmasi", done: status === "confirmed", cancelled: false },
    ];
  }

  const steps = getSteps(mockOrder.status);
  const q = queueLabel[mockQueue.status];

  const orderPrice = mockOrder.totalPrice || total;

  return (
    <div className="flex flex-col gap-4 px-4 py-5">
      <H2>Pesanan Saya</H2>

      <Card>
        <CardContent className="flex flex-col items-center gap-3 py-6 text-center">
          <span className="text-5xl font-bold tracking-tight text-primary-600">
            {mockQueue.queueNumber}
          </span>
          <Muted>Nomor antrian kamu</Muted>
          <Badge variant={q.variant}>{q.label}</Badge>
          <div className="mt-2 grid w-full grid-cols-2 gap-3">
            <div className="rounded-md bg-muted p-3">
              <span className="text-xs text-muted-foreground">Posisi</span>
              <p className="text-lg font-bold">{mockQueue.position} / antrean</p>
            </div>
            <div className="rounded-md bg-muted p-3">
              <span className="text-xs text-muted-foreground">Estimasi</span>
              <p className="text-lg font-bold">~{mockQueue.estimatedWait} menit</p>
            </div>
          </div>
          <span className="text-xs text-muted-foreground">Terakhir diperbarui beberapa detik lalu</span>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Status Pesanan</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4">
            {steps.map((step, idx) => (
              <div key={step.key} className="flex items-start gap-3">
                <span
                  className={cn(
                    "flex size-7 shrink-0 items-center justify-center rounded-full text-xs font-bold",
                    step.done && !step.cancelled && "bg-success text-success-foreground",
                    step.cancelled && "bg-destructive text-destructive-foreground",
                    !step.done && !step.cancelled && "border-2 border-muted-foreground/30 bg-card text-muted-foreground",
                  )}
                >
                  {step.done || step.cancelled ? (
                    step.cancelled ? <CloseIcon className="size-3.5" /> : <CheckIcon className="size-3.5" />
                  ) : (
                    idx + 1
                  )}
                </span>
                <div className="flex flex-col gap-0.5">
                  <span
                    className={cn(
                      "text-sm font-medium",
                      step.cancelled && "text-destructive",
                      !step.done && !step.cancelled && "text-muted-foreground",
                    )}
                  >
                    {step.label}
                  </span>
                  {step.done && (
                    <span className="text-xs text-muted-foreground">{mockOrder.createdAt}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Pesanan Kamu</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-2">
            {mockOrder.items.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between text-sm">
                <span>
                  {item.quantity}x {item.name}
                </span>
                <span className="font-medium">{formatRupiah(item.subtotal)}</span>
              </div>
            ))}
            <hr className="my-2 border-border" />
            <div className="flex items-center justify-between font-bold">
              <span>Total</span>
              <span>{formatRupiah(orderPrice)}</span>
            </div>
            {mockOrder.notes && (
              <p className="mt-2 text-xs text-muted-foreground">
                Catatan: {mockOrder.notes}
              </p>
            )}
            <span className="mt-1 text-xs text-muted-foreground">
              #{mockOrder.id}
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
