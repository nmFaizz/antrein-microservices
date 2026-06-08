"use client";

import Link from "next/link";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import {
  ClockIcon,
  QueueIcon,
  TicketIcon,
  UserIcon,
} from "@/components/ui/icons";
import { ButtonLink } from "@/components/ui/button-link";
import { PageHeader } from "@/components/ui/page-header";
import { StatCard } from "@/components/ui/stat-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { mockQueues, mockSettings } from "@/features/queue/mock";
import { formatQueueNumber } from "@/features/queue/types";
import { formatTime } from "@/lib/format";

export default function DashboardPage() {
  const queues = mockQueues;
  const prefix = mockSettings.prefix;

  const count = (name: string) =>
    queues.filter((q) => q.status_name === name).length;

  const nowServing = queues.find((q) => q.status_name === "called");
  const nextInLine = queues
    .filter((q) => q.status_name === "waiting")
    .sort((a, b) => a.current_position - b.current_position)
    .slice(0, 4);

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Dashboard"
        subtitle={`Ringkasan antrian hari ini · ${queues.length} total antrian`}
        actions={<ButtonLink href="/admin/queues">Kelola Antrian</ButtonLink>}
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          label="Menunggu"
          value={count("waiting")}
          icon={<QueueIcon className="size-5" />}
        />
        <StatCard
          label="Dipanggil"
          value={count("called")}
          icon={<TicketIcon className="size-5" />}
        />
        <StatCard
          label="Selesai"
          value={count("served")}
          icon={<UserIcon className="size-5" />}
        />
        <StatCard
          label="Dilewati"
          value={count("skipped")}
          icon={<ClockIcon className="size-5" />}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Sedang Dilayani</CardTitle>
          </CardHeader>
          <CardContent>
            {nowServing ? (
              <div className="flex flex-col items-center gap-3 py-4 text-center">
                <span className="text-4xl font-bold tracking-tight text-primary-600">
                  {formatQueueNumber(prefix, nowServing.queue_number)}
                </span>
                <span className="font-medium">{nowServing.customer_name}</span>
                <StatusBadge name={nowServing.status_name} />
                <span className="text-xs text-muted-foreground">
                  Dipanggil{" "}
                  {nowServing.called_at && formatTime(nowServing.called_at)}
                </span>
              </div>
            ) : (
              <p className="py-8 text-center text-sm text-muted-foreground">
                Tidak ada antrian yang sedang dipanggil.
              </p>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Antrian Berikutnya</CardTitle>
          </CardHeader>
          <CardContent>
            {nextInLine.length ? (
              <ul className="flex flex-col divide-y divide-border">
                {nextInLine.map((q) => (
                  <li
                    key={q.id}
                    className="flex items-center justify-between gap-3 py-3 first:pt-0 last:pb-0"
                  >
                    <div className="flex items-center gap-3">
                      <span className="flex size-10 items-center justify-center rounded-md bg-muted font-semibold">
                        {formatQueueNumber(prefix, q.queue_number)}
                      </span>
                      <div className="flex flex-col">
                        <span className="text-sm font-medium">
                          {q.customer_name}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          Posisi {q.current_position} · ~
                          {q.estimated_wait_minutes} mnt
                        </span>
                      </div>
                    </div>
                    <Link
                      href={`/admin/queues/${q.id}`}
                      className="text-sm font-medium text-primary-600 hover:underline"
                    >
                      Detail
                    </Link>
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState
                icon={<QueueIcon className="size-6" />}
                title="Antrian kosong"
                description="Belum ada pelanggan yang menunggu."
              />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
