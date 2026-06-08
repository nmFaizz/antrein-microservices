"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { DatePicker } from "@/components/ui/date-picker";
import { Form } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { RadioGroup } from "@/components/ui/radio-group";
import { Select } from "@/components/ui/select";

import { type CreateUserValues, createUserSchema } from "./types";

const roleOptions = [
  { label: "Admin", value: "admin" },
  { label: "Staff", value: "staff" },
  { label: "Viewer", value: "viewer" },
];

const planOptions = [
  { label: "Free", value: "free" },
  { label: "Pro", value: "pro" },
];

/**
 * Demo create-user form. Shows the intended pattern: `useForm` + `zodResolver`
 * drive a `<Form>`, and the field components read everything they need from
 * context — callers only pass `name` (and a label / options).
 */
export function UserForm() {
  const methods = useForm<CreateUserValues>({
    resolver: zodResolver(createUserSchema),
    defaultValues: {
      name: "",
      username: "",
      email: "",
      role: "",
      plan: "",
      bornAt: undefined,
      newsletter: false,
    },
  });

  const onSubmit = (values: CreateUserValues) => {
    // Replace with a useMutation(createUser) call against the real backend.
    console.log("submit", values);
    methods.reset();
  };

  return (
    <Form methods={methods} onSubmit={onSubmit} className="max-w-sm">
      <Input name="name" label="Name" placeholder="Ada Lovelace" />
      <Input name="username" label="Username" placeholder="ada" />
      <Input
        name="email"
        label="Email"
        type="email"
        placeholder="ada@example.com"
      />
      <Select
        name="role"
        label="Role"
        options={roleOptions}
        placeholder="Select a role"
      />
      <RadioGroup name="plan" label="Plan" options={planOptions} />
      <DatePicker<CreateUserValues> name="bornAt" label="Birth date" />
      <Checkbox name="newsletter" label="Subscribe to newsletter" />
      <Button type="submit" disabled={methods.formState.isSubmitting}>
        Submit
      </Button>
    </Form>
  );
}
