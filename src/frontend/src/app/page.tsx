"use client";

import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { H1, H2, Lead, Muted, P } from "@/components/ui/typography";
import { userColumns } from "@/features/users/columns";
import { useUsers } from "@/features/users/queries";
import { UserForm } from "@/features/users/user-form";

export default function Home() {
  const { data: users, isLoading, isError, error } = useUsers();

  return (
    <main className="mx-auto w-full max-w-3xl space-y-10 p-8">
      <header className="space-y-1">
        <H1>Antrein Frontend Boilerplate</H1>
        <Muted>
          Next.js · TanStack Query &amp; Table · Axios · React Hook Form · Zod ·
          Tailwind
        </Muted>
      </header>

      <section className="space-y-4">
        <H2>Components</H2>
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="primary">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="destructive">Destructive</Button>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button size="sm">Small</Button>
          <Button size="md">Medium</Button>
          <Button size="lg">Large</Button>
          <Button disabled>Disabled</Button>
        </div>
        <div className="space-y-1">
          <Lead>Lead paragraph for section intros.</Lead>
          <P>Body text rendered with the P typography component.</P>
          <Muted>Muted helper text.</Muted>
        </div>
      </section>

      <section className="space-y-3">
        <H2>Create user (form fields)</H2>
        <UserForm />
      </section>

      <section className="space-y-3">
        <H2>Users (TanStack Query + Table)</H2>
        {isLoading && <P>Loading…</P>}
        {isError && (
          <p className="text-sm text-destructive">
            {error instanceof Error ? error.message : "Failed to load users"}
          </p>
        )}
        {users && <DataTable columns={userColumns} data={users} />}
      </section>
    </main>
  );
}
