"use client";

import { useFormContext } from "react-hook-form";

import { cn } from "@/lib/utils";

import { controlClassName, Field, useFieldError } from "./field";

interface TextareaProps
  extends Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, "name"> {
  name: string;
  label?: string;
}

/** Multiline text input bound to the surrounding `<Form>` context. */
export function Textarea({ name, label, className, ...props }: TextareaProps) {
  const { register } = useFormContext();
  const error = useFieldError(name);

  return (
    <Field name={name} label={label}>
      <textarea
        id={name}
        aria-invalid={!!error}
        className={cn(controlClassName, "min-h-20 py-2", className)}
        {...register(name)}
        {...props}
      />
    </Field>
  );
}
