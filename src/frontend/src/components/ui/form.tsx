"use client";

import {
  type FieldValues,
  FormProvider,
  type SubmitHandler,
  type UseFormReturn,
} from "react-hook-form";

import { cn } from "@/lib/utils";

/**
 * Wraps a form in a react-hook-form context so field components (`Input`,
 * `Select`, `Checkbox`, …) can read state via `useFormContext` instead of prop
 * drilling.
 *
 * @example
 * import { Form } from "@/components/ui/form";
 * import { Input } from "@/components/ui/input";
 *
 * const methods = useForm<Values>({ resolver: zodResolver(schema) });
 * <Form methods={methods} onSubmit={(values) => ...}>
 *   <Input name="email" label="Email" />
 * </Form>
 */
interface FormProps<TValues extends FieldValues>
  extends Omit<React.FormHTMLAttributes<HTMLFormElement>, "onSubmit"> {
  methods: UseFormReturn<TValues>;
  onSubmit: SubmitHandler<TValues>;
}

export function Form<TValues extends FieldValues>({
  methods,
  onSubmit,
  children,
  className,
  ...props
}: FormProps<TValues>) {
  return (
    <FormProvider {...methods}>
      <form
        onSubmit={methods.handleSubmit(onSubmit)}
        className={cn("space-y-4", className)}
        noValidate
        {...props}
      >
        {children}
      </form>
    </FormProvider>
  );
}
