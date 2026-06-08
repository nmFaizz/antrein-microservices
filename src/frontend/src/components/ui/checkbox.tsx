"use client";

import { useFormContext } from "react-hook-form";

import { cn } from "@/lib/utils";

import { Field, useFieldError } from "./field";

interface CheckboxProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "name" | "type"> {
  name: string;
  label?: string;
}

/** Single checkbox bound to the surrounding `<Form>` context (boolean value). */
export function Checkbox({ name, label, className, ...props }: CheckboxProps) {
  const { register } = useFormContext();
  const error = useFieldError(name);

  return (
    <Field name={name} label={label} inline>
      <input
        id={name}
        type="checkbox"
        aria-invalid={!!error}
        className={cn("size-4 rounded border-input accent-primary", className)}
        {...register(name)}
        {...props}
      />
    </Field>
  );
}
