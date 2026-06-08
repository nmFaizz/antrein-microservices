"use client";

import { useState } from "react";

import { ButtonLink } from "@/components/ui/button-link";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { FilterSelect } from "@/components/ui/filter-select";
import { PageHeader } from "@/components/ui/page-header";
import { Pagination } from "@/components/ui/pagination";
import { SearchInput } from "@/components/ui/search-input";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { Muted } from "@/components/ui/typography";
import { getQueueColumns } from "@/features/queue/columns";
import {
  actionMeta,
  type QueueAction,
  QueueRowActions,
} from "@/features/queue/components/queue-row-actions";
import {
  useCallNext,
  useCancelQueue,
  useQueues,
  useRequeueQueue,
  useServeQueue,
  useSkipQueue,
} from "@/features/queue/queries";
import { type Queue, QUEUE_STATUSES } from "@/features/queue/types";

const PAGE_SIZE = 6;

const statusFilterOptions = [
  { label: "Semua status", value: "" },
  ...QUEUE_STATUSES.map((s) => ({ label: s.replace(/_/g, " "), value: s })),
];

export default function QueuesPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);
  const [pending, setPending] = useState<{
    queue: Queue;
    action: QueueAction;
  } | null>(null);

  const { data: queues = [], isLoading, isError } = useQueues();
  const callNext = useCallNext();
  const serveQueue = useServeQueue();
  const skipQueue = useSkipQueue();
  const requeueQueue = useRequeueQueue();
  const cancelQueue = useCancelQueue();

  const isActing =
    callNext.isPending ||
    serveQueue.isPending ||
    skipQueue.isPending ||
    requeueQueue.isPending ||
    cancelQueue.isPending;

  const filtered = queues.filter((q) => {
    const matchesSearch = (q.customer_name ?? "")
      .toLowerCase()
      .includes(search.toLowerCase());
    const matchesStatus = !status || q.status_name === status;
    return matchesSearch && matchesStatus;
  });

  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(page, pageCount);
  const pageRows = filtered.slice(
    (safePage - 1) * PAGE_SIZE,
    safePage * PAGE_SIZE,
  );

  async function applyAction(queue: Queue, action: QueueAction) {
    setPending(null);
    switch (action) {
      case "call":
        // individual call — not used via row, only via call-next button
        break;
      case "serve":
        await serveQueue.mutateAsync(queue.id);
        break;
      case "skip":
        await skipQueue.mutateAsync({ id: queue.id });
        break;
      case "requeue":
        await requeueQueue.mutateAsync(queue.id);
        break;
      case "cancel":
        await cancelQueue.mutateAsync(queue.id);
        break;
    }
  }

  const waitingCount = queues.filter((q) => q.status_name === "waiting").length;

  const columns = getQueueColumns("A", (queue) => (
    <QueueRowActions
      queue={queue}
      onAction={(q, action) => setPending({ queue: q, action })}
    />
  ));

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Manajemen Antrian"
        subtitle={`${waitingCount} menunggu`}
        actions={
          <div className="flex items-center gap-2">
            <ButtonLink href="/admin/settings" variant="outline">
              Pengaturan
            </ButtonLink>
            <Button
              onClick={() => callNext.mutate()}
              disabled={waitingCount === 0 || isActing}
            >
              {callNext.isPending ? "Memanggil…" : "Panggil Berikutnya"}
            </Button>
          </div>
        }
      />

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <SearchInput
          className="sm:max-w-xs"
          placeholder="Cari pelanggan…"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
        <FilterSelect
          options={statusFilterOptions}
          placeholder="Semua status"
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
            setPage(1);
          }}
        />
        <span className="text-sm text-muted-foreground sm:ml-auto">
          {filtered.length} antrian
        </span>
      </div>

      {isLoading && (
        <div className="flex flex-col gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            // biome-ignore lint/suspicious/noArrayIndexKey: skeleton
            <div key={i} className="h-12 animate-pulse rounded-lg bg-muted" />
          ))}
        </div>
      )}

      {isError && <Muted>Gagal memuat antrian. Coba lagi nanti.</Muted>}

      {!isLoading && !isError && (
        <>
          <DataTable
            columns={columns}
            data={pageRows}
            emptyMessage="Tidak ada antrian yang cocok."
          />
          <Pagination
            page={safePage}
            pageCount={pageCount}
            onPageChange={setPage}
          />
        </>
      )}

      {pending && (
        <ConfirmDialog
          open
          onClose={() => setPending(null)}
          onConfirm={() => applyAction(pending.queue, pending.action)}
          title={actionMeta[pending.action].title}
          description={actionMeta[pending.action].description}
          confirmLabel="Ya, lanjutkan"
          cancelLabel="Batal"
          confirmVariant={actionMeta[pending.action].variant}
        />
      )}
    </div>
  );
}
