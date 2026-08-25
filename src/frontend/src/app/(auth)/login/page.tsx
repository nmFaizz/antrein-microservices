"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { QueueIcon } from "@/components/ui/icons";
import { getMe, login } from "@/features/auth/api";
import { type LoginValues, loginSchema } from "@/features/auth/types";
import { setRole, setToken } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  const methods = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
  });

  async function onSubmit(values: LoginValues) {
    setError(null);
    try {
      const token = await login(values);
      setToken(token.access_token); // cookie set before getMe so interceptor picks it up
      const user = await getMe();
      setRole(user.role);
      router.push(user.role === "admin" ? "/admin/dashboard" : "/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  }

  return (
    <div className="space-y-8">
      <header className="space-y-3">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-primary-700">
          AntreIn account
        </p>
        <h1 className="text-4xl font-semibold leading-[1.02] tracking-[-0.06em] text-balance sm:text-5xl">
          Welcome back.
        </h1>
        <p className="max-w-md text-base leading-7 text-muted-foreground">
          Sign in to browse the menu, place a pre-order, or manage today&apos;s
          queue.
        </p>
      </header>

      <section
        aria-labelledby="login-form-title"
        className="rounded-[1.75rem] border border-border/80 bg-card p-6 shadow-[0_24px_60px_-38px_rgba(28,25,23,0.55)] sm:p-8"
      >
        <div className="mb-7 flex items-start justify-between gap-4">
          <div>
            <h2
              id="login-form-title"
              className="text-lg font-semibold tracking-tight"
            >
              Sign in
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Use your AntreIn credentials.
            </p>
          </div>
          <span className="hidden items-center gap-1.5 rounded-full bg-secondary px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground sm:flex">
            <span className="size-1.5 rounded-full bg-success" />
            Ready
          </span>
        </div>

        <Form
          methods={methods}
          onSubmit={onSubmit}
          aria-label="Sign in to AntreIn"
          aria-busy={methods.formState.isSubmitting}
          className="space-y-5"
        >
          <Input
            name="username"
            label="Username"
            autoComplete="username"
            className="h-12 rounded-xl border-border/80 bg-background px-4 text-base shadow-none focus:border-primary-600 focus:ring-4 focus:ring-primary/15"
          />
          <Input
            name="password"
            label="Password"
            type="password"
            autoComplete="current-password"
            className="h-12 rounded-xl border-border/80 bg-background px-4 text-base shadow-none focus:border-primary-600 focus:ring-4 focus:ring-primary/15"
          />
          {error && (
            <div
              role="alert"
              aria-live="polite"
              className="flex items-start gap-3 rounded-xl border border-destructive/20 bg-destructive/5 px-4 py-3 text-sm leading-5 text-destructive"
            >
              <span
                aria-hidden="true"
                className="mt-1 size-2 shrink-0 rounded-full bg-destructive"
              />
              <p>{error}</p>
            </div>
          )}
          <Button
            type="submit"
            size="lg"
            className="h-12 w-full rounded-xl bg-primary font-semibold shadow-[0_12px_24px_-16px_rgba(202,138,4,0.9)] transition-[transform,background-color,box-shadow] hover:-translate-y-0.5 hover:bg-primary-500 hover:shadow-[0_16px_28px_-16px_rgba(202,138,4,0.9)] active:translate-y-px"
            disabled={methods.formState.isSubmitting}
          >
            {methods.formState.isSubmitting ? "Signing in…" : "Sign in"}
          </Button>
        </Form>
      </section>

      <div className="flex items-center gap-3 text-sm text-muted-foreground">
        <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary/15 text-primary-700">
          <QueueIcon className="size-4" />
        </span>
        <p>
          One account for menus, pre-orders, and queue updates.
        </p>
      </div>

      <p className="text-sm text-muted-foreground">
        Don&apos;t have an account?{" "}
        <Link
          href="/register"
          className="rounded-sm font-semibold text-foreground underline decoration-primary underline-offset-4 outline-none transition-colors hover:text-primary-700 focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
        >
          Create an account
        </Link>
      </p>
    </div>
  );
}
