import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  /** Display name of the (customizable) queue status, e.g. "waiting". */
  name: string;
  /** Hex color from the status record, e.g. "#9CA3AF". */
  color?: string | null;
  className?: string;
}

const FALLBACK = "#78716c"; // stone-500

/**
 * Pill for a customizable queue status. Colors are arbitrary hex from the
 * backend, so they're applied via inline style (text = color, bg = ~12% tint)
 * rather than Tailwind tokens.
 */
export function StatusBadge({ name, color, className }: StatusBadgeProps) {
  const base = color || FALLBACK;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium capitalize",
        className,
      )}
      style={{ color: base, backgroundColor: `${base}1f` }}
    >
      <span
        className="size-1.5 rounded-full"
        style={{ backgroundColor: base }}
      />
      {name.replace(/_/g, " ")}
    </span>
  );
}
