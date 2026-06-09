"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { getMe, login } from "@/features/auth/api";
import { type LoginValues, loginSchema } from "@/features/auth/types";
import { setRole, setToken } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  const methods = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
  });

  async function onSubmit(values: LoginValues) {
    setError(null);
    try {
      const token = await login(values);
      setToken(token.access_token); // cookie set before getMe so interceptor picks it up
      const user = await getMe();
      setRole(user.role);
      router.push(user.role === "admin" ? "/admin/dashboard" : "/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  }

  return (
    <div className="space-y-6">
      <div className="space-y-1 text-center">
        <h1 className="text-2xl font-bold tracking-tight">Welcome back</h1>
        <p className="text-sm text-muted-foreground">Sign in to your account</p>
      </div>

      <Form methods={methods} onSubmit={onSubmit}>
        <Input name="username" label="Username" autoComplete="username" />
        <Input
          name="password"
          label="Password"
          type="password"
          autoComplete="current-password"
        />
        {error && <p className="text-sm text-destructive">{error}</p>}
        <Button
          type="submit"
          className="w-full"
          disabled={methods.formState.isSubmitting}
        >
          {methods.formState.isSubmitting ? "Signing in…" : "Sign in"}
        </Button>
      </Form>

      <p className="text-center text-sm text-muted-foreground">
        Don&apos;t have an account?{" "}
        <Link
          href="/register"
          className="font-medium underline underline-offset-4"
        >
          Register
        </Link>
      </p>
    </div>
  );
}
