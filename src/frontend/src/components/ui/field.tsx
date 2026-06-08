"use client";

import {
  type FieldError as RHFFieldError,
  useFormContext,
} from "react-hook-form";

import { cn } from "@/lib/utils";

/** Base styling shared by text-like controls (input, textarea, select). */
export const controlClassName =
  "w-full rounded-md border border-input bg-background px-3 text-sm outline-none transition placeholder:text-muted-foreground focus:border-ring focus:ring-2 focus:ring-ring/30 aria-[invalid=true]:border-destructive";

/** Read a (possibly nested, e.g. "address.city") field error from form state. */
export function useFieldError(name: string): RHFFieldError | undefined {
  const {
    formState: { errors },
  } = useFormContext();
  return name
    .split(".")
    .reduce<unknown>(
      (acc, key) => (acc as Record<string, unknown>)?.[key],
      errors,
    ) as RHFFieldError | undefined;
}

export function Label({
  className,
  ...props
}: React.LabelHTMLAttributes<HTMLLabelElement>) {
  return (
    // biome-ignore lint/a11y/noLabelWithoutControl: htmlFor is supplied by callers
    <label className={cn("text-sm font-medium", className)} {...props} />
  );
}

export function FieldError({ error }: { error?: RHFFieldError }) {
  if (!error?.message) return null;
  return <p className="text-xs text-destructive">{String(error.message)}</p>;
}

interface FieldProps {
  name: string;
  label?: string;
  /** Render the label after the control (used by checkboxes). */
  inline?: boolean;
  className?: string;
  children: React.ReactNode;
}

/**
 * Shared layout for a form field: label + control slot + error message.
 * Field components compose this instead of re-implementing the wrapper.
 */
export function Field({
  name,
  label,
  inline,
  className,
  children,
}: FieldProps) {
  const error = useFieldError(name);

  if (inline) {
    return (
      <div className={cn("flex flex-col gap-1.5", className)}>
        <div className="flex items-center gap-2">
          {children}
          {label && <Label htmlFor={name}>{label}</Label>}
        </div>
        <FieldError error={error} />
      </div>
    );
  }

  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      {label && <Label htmlFor={name}>{label}</Label>}
      {children}
      <FieldError error={error} />
    </div>
  );
}
