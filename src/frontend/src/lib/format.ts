/** Shared display formatters (locale: id-ID). */

const rupiah = new Intl.NumberFormat("id-ID", {
  style: "currency",
  currency: "IDR",
  maximumFractionDigits: 0,
});

export function formatRupiah(value: number): string {
  return rupiah.format(value);
}

/** "8 Jun 2026" */
export function formatDate(value: string | Date): string {
  const date = typeof value === "string" ? new Date(value) : value;
  return date.toLocaleDateString("id-ID", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

/** "14:05" */
export function formatTime(value: string | Date): string {
  const date = typeof value === "string" ? new Date(value) : value;
  return date.toLocaleTimeString("id-ID", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** "8 Jun 2026, 14:05" */
export function formatDateTime(value: string | Date): string {
  return `${formatDate(value)}, ${formatTime(value)}`;
}

/**
 * Converts an absolute estimated-time ISO string (from the queue service)
 * into a human-readable remaining-time label.
 * e.g. "~5 menit" | "~1 jam 10 menit" | "Segera"
 */
export function formatEstimatedTime(value: string): string {
  const diffMin = Math.round((new Date(value).getTime() - Date.now()) / 60_000);
  if (diffMin <= 0) return "Segera";
  if (diffMin < 60) return `~${diffMin} menit`;
  const h = Math.floor(diffMin / 60);
  const m = diffMin % 60;
  return m > 0 ? `~${h} jam ${m} menit` : `~${h} jam`;
}
