"use client";

import { useFormContext } from "react-hook-form";

import { cn } from "@/lib/utils";

import { Field, useFieldError } from "./field";

interface SwitchProps {
  name: string;
  label?: string;
  className?: string;
}

/**
 * Toggle switch bound to the surrounding `<Form>` context (boolean value).
 * Visually a track + thumb; the real control is a peer checkbox for a11y.
 */
export function Switch({ name, label, className }: SwitchProps) {
  const { register } = useFormContext();
  const error = useFieldError(name);

  return (
    <Field name={name} label={label} inline>
      <label className={cn("relative inline-flex cursor-pointer", className)}>
        <input
          id={name}
          type="checkbox"
          aria-invalid={!!error}
          className="peer sr-only"
          {...register(name)}
        />
        <span className="h-6 w-11 rounded-full bg-input transition-colors peer-checked:bg-primary peer-focus-visible:ring-2 peer-focus-visible:ring-ring/40" />
        <span className="absolute left-0.5 top-0.5 size-5 rounded-full bg-white shadow transition-transform peer-checked:translate-x-5" />
      </label>
    </Field>
  );
}
