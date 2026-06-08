import type { ReactNode } from "react";

import { cn } from "@/lib/utils";
import { H2 } from "@/components/ui/typography";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  /** Right-aligned action slot (buttons, etc.). */
  actions?: ReactNode;
  className?: string;
}

/** Standard page title block: heading + optional subtitle + actions. */
export function PageHeader({
  title,
  subtitle,
  actions,
  className,
}: PageHeaderProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between",
        className,
      )}
    >
      <div className="flex flex-col gap-1">
        <H2>{title}</H2>
        {subtitle && (
          <p className="text-sm text-muted-foreground">{subtitle}</p>
        )}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}
