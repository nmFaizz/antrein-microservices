"use client";

import { useFormContext } from "react-hook-form";

import { cn } from "@/lib/utils";

import { controlClassName, Field, useFieldError } from "./field";

interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "name"> {
  name: string;
  label?: string;
}

/**
 * Text input bound to the surrounding `<Form>` context. Registers itself and
 * renders its own label + validation error — callers only pass `name`.
 *
 * @example
 * <Input name="email" label="Email" type="email" />
 */
export function Input({ name, label, type, className, ...props }: InputProps) {
  const { register } = useFormContext();
  const error = useFieldError(name);
  const isNum = type === "number";

  return (
    <Field name={name} label={label}>
      <input
        id={name}
        type={type}
        aria-invalid={!!error}
        className={cn(controlClassName, "h-10", className)}
        {...register(name, { valueAsNumber: isNum })}
        {...props}
      />
    </Field>
  );
}
