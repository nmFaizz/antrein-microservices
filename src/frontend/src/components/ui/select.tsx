"use client";

import { useFormContext } from "react-hook-form";

import { cn } from "@/lib/utils";

import { controlClassName, Field, useFieldError } from "./field";

export interface SelectOption {
  label: string;
  value: string;
}

interface SelectProps
  extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, "name"> {
  name: string;
  label?: string;
  options: SelectOption[];
  placeholder?: string;
}

/** Styled native `<select>` bound to the surrounding `<Form>` context. */
export function Select({
  name,
  label,
  options,
  placeholder,
  className,
  ...props
}: SelectProps) {
  const { register } = useFormContext();
  const error = useFieldError(name);

  return (
    <Field name={name} label={label}>
      <select
        id={name}
        aria-invalid={!!error}
        className={cn(controlClassName, "h-10", className)}
        defaultValue=""
        {...register(name)}
        {...props}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </Field>
  );
}
