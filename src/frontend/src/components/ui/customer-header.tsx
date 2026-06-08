import Link from "next/link";

/** Customer top brand bar (mobile-friendly). */
export function CustomerHeader() {
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-border bg-card/90 px-4 backdrop-blur">
      <Link href="/menu" className="flex items-center gap-2">
        <span className="flex size-7 items-center justify-center rounded-md bg-primary text-sm font-bold text-primary-foreground">
          A
        </span>
        <span className="font-bold tracking-tight">AntreIn</span>
      </Link>
      <Link
        href="/admin/dashboard"
        className="text-xs font-medium text-muted-foreground transition hover:text-foreground"
      >
        Admin
      </Link>
    </header>
  );
}
