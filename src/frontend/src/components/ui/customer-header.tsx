"use client";

import { useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { useCurrentUser } from "@/features/auth/hooks";
import { clearToken } from "@/lib/auth";

import { LogOutIcon, UserIcon } from "./icons";

/** Customer top brand bar (mobile-friendly). */
export function CustomerHeader() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { data: user } = useCurrentUser();

  function handleLogout() {
    clearToken();
    queryClient.clear();
    router.push("/login");
  }

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-border bg-card/90 px-4 backdrop-blur">
      <Link href="/menu" className="flex items-center gap-2">
        <span className="flex size-7 items-center justify-center rounded-md bg-primary text-sm font-bold text-primary-foreground">
          A
        </span>
        <span className="font-bold tracking-tight">AntreIn</span>
      </Link>

      <div className="flex items-center gap-3">
        {user && (
          <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <UserIcon className="size-4" />
            <span className="font-medium text-foreground">{user.username}</span>
          </div>
        )}
        <button
          type="button"
          onClick={handleLogout}
          className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground transition hover:text-destructive"
          aria-label="Logout"
        >
          <LogOutIcon className="size-4" />
          <span className="hidden sm:inline">Logout</span>
        </button>
      </div>
    </header>
  );
}
