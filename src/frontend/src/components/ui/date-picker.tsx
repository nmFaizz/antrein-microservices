"use client";

import { useEffect, useRef, useState } from "react";
import { type FieldValues, type Path, useController } from "react-hook-form";

import { cn } from "@/lib/utils";

import { Calendar } from "./calendar";
import { controlClassName, Field } from "./field";

interface DatePickerProps<TValues extends FieldValues> {
  name: Path<TValues>;
  label?: string;
  placeholder?: string;
  className?: string;
}

/**
 * Calendar-backed date select bound to the surrounding `<Form>` context. Stores
 * a `Date` value via `useController`; opens a popover with `<Calendar>`.
 *
 * @example
 * <DatePicker<FormValues> name="bornAt" label="Birth date" />
 */
export function DatePicker<TValues extends FieldValues>({
  name,
  label,
  placeholder = "Pick a date",
  className,
}: DatePickerProps<TValues>) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const {
    field: { value, onChange },
    fieldState: { error },
  } = useController<TValues>({ name });

  const selected = value as Date | undefined;

  // Close the popover when clicking outside of it.
  useEffect(() => {
    if (!open) return;
    function onPointerDown(event: MouseEvent) {
      if (!containerRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onPointerDown);
    return () => document.removeEventListener("mousedown", onPointerDown);
  }, [open]);

  return (
    <Field name={name} label={label} className={className}>
      <div ref={containerRef} className="relative">
        <button
          type="button"
          aria-invalid={!!error}
          onClick={() => setOpen((prev) => !prev)}
          className={cn(controlClassName, "h-10 text-left")}
        >
          {selected ? (
            selected.toLocaleDateString()
          ) : (
            <span className="text-black/40 dark:text-white/40">
              {placeholder}
            </span>
          )}
        </button>
        {open && (
          <div className="absolute z-10 mt-1 rounded-md border border-black/10 bg-background shadow-lg dark:border-white/15">
            <Calendar
              mode="single"
              selected={selected}
              onSelect={(date) => {
                onChange(date);
                setOpen(false);
              }}
              autoFocus
            />
          </div>
        )}
      </div>
    </Field>
  );
}
