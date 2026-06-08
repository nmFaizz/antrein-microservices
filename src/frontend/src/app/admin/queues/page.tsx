"use client";

import { useMemo, useState } from "react";

import { ButtonLink } from "@/components/ui/button-link";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { FilterSelect } from "@/components/ui/filter-select";
import { PageHeader } from "@/components/ui/page-header";
import { Pagination } from "@/components/ui/pagination";
import { SearchInput } from "@/components/ui/search-input";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { getQueueColumns } from "@/features/queue/columns";
import {
  actionMeta,
  type QueueAction,
  QueueRowActions,
} from "@/features/queue/components/queue-row-actions";
import { mockQueues, mockSettings } from "@/features/queue/mock";
import { type Queue, QUEUE_STATUSES } from "@/features/queue/types";

const PAGE_SIZE = 6;

const statusFilterOptions = QUEUE_STATUSES.map((s) => ({
  label: s.replace(/_/g, " "),
  value: s,
}));

export default function QueuesPage() {
  const [queues, setQueues] = useState<Queue[]>(mockQueues);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);
  const [pending, setPending] = useState<{
    queue: Queue;
    action: QueueAction;
  } | null>(null);

  const filtered = useMemo(() => {
    return queues.filter((q) => {
      const matchesSearch = (q.customer_name ?? "")
        .toLowerCase()
        .includes(search.toLowerCase());
      const matchesStatus = !status || q.status_name === status;
      return matchesSearch && matchesStatus;
    });
  }, [queues, search, status]);

  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(page, pageCount);
  const pageRows = filtered.slice(
    (safePage - 1) * PAGE_SIZE,
    safePage * PAGE_SIZE,
  );

  function applyAction(queue: Queue, action: QueueAction) {
    // TODO: integrate POST /queues/{id}/{call|serve|skip|requeue|cancel}
    const next = actionMeta[action].nextStatus;
    setQueues((prev) =>
      prev.map((q) => (q.id === queue.id ? { ...q, status_name: next } : q)),
    );
  }

  function callNext() {
    // TODO: integrate POST /queues/call-next
    const target = queues
      .filter((q) => q.status_name === "waiting")
      .sort((a, b) => {
        // Prioritize checked-in, then position.
        if (a.is_checked_in !== b.is_checked_in) {
          return a.is_checked_in ? -1 : 1;
        }
        return a.current_position - b.current_position;
      })[0];
    if (target) applyAction(target, "call");
  }

  const columns = getQueueColumns(mockSettings.prefix, (queue) => (
    <QueueRowActions
      queue={queue}
      onAction={(q, action) => setPending({ queue: q, action })}
    />
  ));

  const waitingCount = queues.filter((q) => q.status_name === "waiting").length;

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Manajemen Antrian"
        subtitle={`${mockSettings.prefix} · ${waitingCount} menunggu`}
        actions={
          <div className="flex items-center gap-2">
            <ButtonLink href="/admin/settings" variant="outline">
              Pengaturan
            </ButtonLink>
            <Button onClick={callNext} disabled={waitingCount === 0}>
              Panggil Berikutnya
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
