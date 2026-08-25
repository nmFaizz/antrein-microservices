import { ClockIcon, QueueIcon, TicketIcon } from "@/components/ui/icons";
import { AuthBrand } from "@/components/auth/auth-brand";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-dvh bg-background lg:grid lg:grid-cols-[minmax(0,0.92fr)_minmax(28rem,1.08fr)]">
      <aside
        aria-labelledby="auth-panel-title"
        className="relative hidden min-h-dvh overflow-hidden bg-foreground text-background lg:flex lg:flex-col lg:justify-between lg:p-10 xl:p-14"
      >
        <div
          className="pointer-events-none absolute inset-0"
          aria-hidden="true"
        >
          <div className="absolute -right-48 -top-48 size-[34rem] rounded-full border border-background/10" />
          <div className="absolute -right-20 top-24 size-56 rounded-full border border-primary/15" />
          <div className="absolute bottom-16 left-1/3 size-72 rounded-full border border-background/5" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_78%_0%,rgba(250,204,21,0.16),transparent_34%)]" />
          <span className="absolute -bottom-16 -left-8 text-[19rem] font-bold leading-none tracking-[-0.16em] text-background/[0.035]">
            A
          </span>
        </div>

        <div className="relative z-10 flex items-center justify-between gap-4">
          <AuthBrand inverse />
          <span className="rounded-full border border-background/15 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-background/60">
            Queue flow
          </span>
        </div>

        <div className="relative z-10 my-auto max-w-xl py-20 xl:py-28">
          <p className="mb-5 text-xs font-semibold uppercase tracking-[0.24em] text-primary-300">
            Less waiting. More doing.
          </p>
          <h1
            id="auth-panel-title"
            className="max-w-lg text-5xl font-semibold leading-[0.98] tracking-[-0.07em] text-balance xl:text-7xl"
          >
            Skip the line.
            <br />
            <span className="text-primary">Keep your time.</span>
          </h1>
          <p className="mt-7 max-w-md text-base leading-7 text-background/65">
            Browse the menu, place a pre-order, and keep your place in line from
            one calm, simple space.
          </p>
        </div>

        <div className="relative z-10 space-y-5">
          <div className="flex items-center justify-between gap-4 border-t border-background/10 pt-4 text-xs text-background/45">
            <span>Food, queues, sorted.</span>
            <span className="flex items-center gap-2">
              <QueueIcon className="size-3.5" />
              AntreIn platform
            </span>
          </div>
        </div>
      </aside>

      <main className="relative flex min-h-dvh flex-col overflow-hidden">
        <div
          className="pointer-events-none absolute inset-0"
          aria-hidden="true"
        >
          <div className="absolute -right-24 -top-24 size-72 rounded-full bg-primary/10 blur-3xl" />
          <div className="absolute bottom-0 left-1/2 size-80 -translate-x-1/2 rounded-full bg-primary/[0.04] blur-3xl" />
        </div>

        <div className="relative z-10 mx-auto flex w-full max-w-2xl flex-1 flex-col justify-center px-6 py-8 sm:px-10 sm:py-12 lg:px-12 xl:px-16">
          <div className="mb-12 lg:hidden">
            <AuthBrand />
          </div>
          <div className="w-full max-w-lg">{children}</div>
          <p className="mt-10 text-center text-xs leading-5 text-muted-foreground/80">
            A simpler way to move through menus, pre-orders, and queues.
          </p>
        </div>
      </main>
    </div>
  );
}
