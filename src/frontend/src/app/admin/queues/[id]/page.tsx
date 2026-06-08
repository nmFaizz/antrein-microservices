"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { ButtonLink } from "@/components/ui/button-link";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { BellIcon, ChevronLeftIcon, UserIcon } from "@/components/ui/icons";
import { StatusBadge } from "@/components/ui/status-badge";
import { Tab, TabList, TabPanel, Tabs } from "@/components/ui/tabs";
import {
  mockNotifications,
  mockQueues,
  mockSettings,
  mockStatusLogs,
} from "@/features/queue/mock";
import {
  formatQueueNumber,
  type QueueStatusLog,
} from "@/features/queue/types";
import { formatDateTime, formatTime } from "@/lib/format";

const triggerBadge: Record<string, "info" | "warning" | "muted"> = {
  admin: "info",
  customer: "warning",
  system: "muted",
};

/** Build a timeline from explicit logs, or derive one from the queue's timestamps. */
function buildTimeline(queueId: string): QueueStatusLog[] {
  const explicit = mockStatusLogs.filter((l) => l.queue_id === queueId);
  if (explicit.length) return explicit;
  const queue = mockQueues.find((q) => q.id === queueId);
  if (!queue) return [];
  const logs: QueueStatusLog[] = [
    {
      id: `${queueId}-created`,
      queue_id: queueId,
      previous_status: null,
      new_status: "waiting",
      triggered_by: null,
      trigger_type: "system",
      notes: "Antrian dibuat",
      created_at: queue.created_at,
    },
  ];
  if (queue.called_at)
    logs.push({
      id: `${queueId}-called`,
      queue_id: queueId,
      previous_status: "waiting",
      new_status: "called",
      triggered_by: queue.called_by,
      trigger_type: "admin",
      notes: null,
      created_at: queue.called_at,
    });
  if (queue.served_at)
    logs.push({
      id: `${queueId}-served`,
      queue_id: queueId,
      previous_status: "called",
      new_status: "served",
      triggered_by: queue.served_by,
      trigger_type: "admin",
      notes: null,
      created_at: queue.served_at,
    });
  if (queue.cancelled_at)
    logs.push({
      id: `${queueId}-cancelled`,
      queue_id: queueId,
      previous_status: "waiting",
      new_status: "cancelled",
      triggered_by: queue.user_id,
      trigger_type: "customer",
      notes: null,
      created_at: queue.cancelled_at,
    });
  return logs;
}

export default function QueueDetailPage() {
  const params = useParams<{ id: string }>();
  const queue = mockQueues.find((q) => q.id === params.id);

  if (!queue) {
    return (
      <EmptyState
        title="Antrian tidak ditemukan"
        description="Antrian mungkin sudah dihapus atau ID tidak valid."
        action={<ButtonLink href="/admin/queues">Kembali ke daftar</ButtonLink>}
      />
    );
  }

  const logs = buildTimeline(queue.id);
  const notifications = mockNotifications.filter(
    (n) => n.queue_id === queue.id,
  );

  return (
    <div className="flex flex-col gap-6">
      <Link
        href="/admin/queues"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground transition hover:text-foreground"
      >
        <ChevronLeftIcon className="size-4" /> Daftar antrian
      </Link>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardContent className="flex flex-col items-center gap-3 text-center">
            <span className="text-5xl font-bold tracking-tight text-primary-600">
              {formatQueueNumber(mockSettings.prefix, queue.queue_number)}
            </span>
            <StatusBadge name={queue.status_name} />
            {queue.is_requeued && (
              <Badge variant="default">Re-queue</Badge>
            )}
            <div className="mt-2 flex w-full items-center gap-3 rounded-md bg-muted p-3 text-left">
              <span className="flex size-9 items-center justify-center rounded-full bg-card text-muted-foreground">
                <UserIcon className="size-5" />
              </span>
              <div className="flex flex-col">
                <span className="text-sm font-medium">
                  {queue.customer_name}
                </span>
                <span className="text-xs text-muted-foreground">
                  {queue.is_checked_in ? "Sudah check-in" : "Belum check-in"}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Informasi Antrian</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-x-6 gap-y-4 text-sm">
            <Info label="Tanggal" value={queue.queue_date} />
            <Info
              label="Posisi saat ini"
              value={
                queue.status_name === "waiting"
                  ? `#${queue.current_position}`
                  : "—"
              }
            />
            <Info
              label="Estimasi tunggu"
              value={
                queue.estimated_wait_minutes > 0
                  ? `${queue.estimated_wait_minutes} menit`
                  : "—"
              }
            />
            <Info
              label="Check-in"
              value={
                queue.checked_in_at ? formatTime(queue.checked_in_at) : "—"
              }
            />
            <Info
              label="Dipanggil"
              value={queue.called_at ? formatTime(queue.called_at) : "—"}
            />
            <Info
              label="Dilayani"
              value={queue.served_at ? formatTime(queue.served_at) : "—"}
            />
            <Info
              label="Pre-order"
              value={queue.preorder_id ? `#${queue.preorder_id}` : "Tanpa pre-order"}
            />
            <Info label="Dibuat" value={formatDateTime(queue.created_at)} />
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="logs">
        <TabList>
          <Tab value="logs">Riwayat Status</Tab>
          <Tab value="notifications">Notifikasi</Tab>
        </TabList>

        <TabPanel value="logs">
          <Card>
            <CardContent>
              {logs.length ? (
                <ol className="relative flex flex-col gap-5 border-l border-border pl-6">
                  {logs.map((log) => (
                    <li key={log.id} className="relative">
                      <span className="absolute -left-[1.69rem] top-1 size-3 rounded-full border-2 border-card bg-primary" />
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-sm font-medium capitalize">
                          {log.previous_status
                            ? `${log.previous_status.replace(/_/g, " ")} → `
                            : ""}
                          {log.new_status.replace(/_/g, " ")}
                        </span>
                        <Badge variant={triggerBadge[log.trigger_type]}>
                          {log.trigger_type}
                        </Badge>
                        <span className="ml-auto text-xs text-muted-foreground">
                          {formatDateTime(log.created_at)}
                        </span>
                      </div>
                      {log.notes && (
                        <p className="mt-1 text-sm text-muted-foreground">
                          {log.notes}
                        </p>
                      )}
                    </li>
                  ))}
                </ol>
              ) : (
                <EmptyState title="Belum ada riwayat status" />
              )}
            </CardContent>
          </Card>
        </TabPanel>

        <TabPanel value="notifications">
          <Card>
            <CardContent>
              {notifications.length ? (
                <ul className="flex flex-col divide-y divide-border">
                  {notifications.map((n) => (
                    <li
                      key={n.id}
                      className="flex items-start gap-3 py-3 first:pt-0 last:pb-0"
                    >
                      <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary-100 text-primary-700">
                        <BellIcon className="size-4" />
                      </span>
                      <div className="flex flex-col">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium capitalize">
                            {n.notification_type}
                          </span>
                          <Badge
                            variant={n.status === "sent" ? "success" : "muted"}
                          >
                            {n.status}
                          </Badge>
                        </div>
                        <span className="text-sm text-muted-foreground">
                          {n.message}
                        </span>
                        {n.sent_at && (
                          <span className="text-xs text-muted-foreground">
                            {formatDateTime(n.sent_at)}
                          </span>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <EmptyState title="Belum ada notifikasi" />
              )}
            </CardContent>
          </Card>
        </TabPanel>
      </Tabs>
    </div>
  );
}

function Info({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}
