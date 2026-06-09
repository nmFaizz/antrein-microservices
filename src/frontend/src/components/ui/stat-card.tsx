import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

import { Card } from "./card";

interface StatCardProps {
  label: string;
  value: ReactNode;
  hint?: string;
  icon?: ReactNode;
  className?: string;
}

export function StatCard({
  label,
  value,
  hint,
  icon,
  className,
}: StatCardProps) {
  return (
    <Card className={cn("p-5", className)}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-col gap-1">
          <span className="text-sm text-muted-foreground">{label}</span>
          <span className="text-2xl font-bold tracking-tight">{value}</span>
          {hint && (
            <span className="text-xs text-muted-foreground">{hint}</span>
          )}
        </div>
        {icon && (
          <span className="flex size-10 shrink-0 items-center justify-center rounded-md bg-primary-100 text-primary-700">
            {icon}
          </span>
        )}
      </div>
    </Card>
  );
}
