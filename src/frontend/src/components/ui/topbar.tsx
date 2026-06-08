import { BellIcon, UserIcon } from "./icons";

/** Admin top bar: spacer + notifications + mock user. */
export function Topbar() {
  return (
    <header className="flex h-16 shrink-0 items-center justify-between gap-4 border-b border-border bg-card px-5">
      <div className="flex items-center gap-2 lg:hidden">
        <span className="flex size-8 items-center justify-center rounded-md bg-primary font-bold text-primary-foreground">
          A
        </span>
        <span className="font-bold tracking-tight">AntreIn</span>
      </div>
      <div className="ml-auto flex items-center gap-3">
        <button
          type="button"
          className="relative flex size-9 items-center justify-center rounded-md text-muted-foreground transition hover:bg-accent hover:text-foreground"
          aria-label="Notifikasi"
        >
          <BellIcon className="size-5" />
          <span className="absolute right-2 top-2 size-2 rounded-full bg-destructive" />
        </button>
        <div className="flex items-center gap-2">
          <span className="flex size-9 items-center justify-center rounded-full bg-primary-100 text-primary-700">
            <UserIcon className="size-5" />
          </span>
          <div className="hidden flex-col leading-tight sm:flex">
            <span className="text-sm font-medium">Admin Resto</span>
            <span className="text-xs text-muted-foreground">Staff</span>
          </div>
        </div>
      </div>
    </header>
  );
}
