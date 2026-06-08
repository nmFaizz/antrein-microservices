"use client";

import { useFormContext } from "react-hook-form";

import { cn } from "@/lib/utils";

import { Field } from "./field";

export interface RadioOption {
  label: string;
  value: string;
}

interface RadioGroupProps {
  name: string;
  label?: string;
  options: RadioOption[];
  className?: string;
}

/**
 * A set of radio buttons bound to one field in the surrounding `<Form>` context.
 * All buttons share `name` so exactly one value is selected.
 */
export function RadioGroup({
  name,
  label,
  options,
  className,
}: RadioGroupProps) {
  const { register } = useFormContext();

  return (
    <Field name={name} label={label}>
      <div className={cn("flex flex-col gap-2", className)}>
        {options.map((option) => {
          const id = `${name}-${option.value}`;
          return (
            <label
              key={option.value}
              htmlFor={id}
              className="flex items-center gap-2 text-sm"
            >
              <input
                id={id}
                type="radio"
                value={option.value}
                className="size-4 accent-foreground"
                {...register(name)}
              />
              {option.label}
            </label>
          );
        })}
      </div>
    </Field>
  );
}
