"use client";

import { SearchIcon } from "@/components/ui/icons";
import { cn } from "@/lib/utils";

interface SearchInputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> {
  className?: string;
}

export function SearchInput({
  className,
  placeholder = "Search…",
  ...props
}: SearchInputProps) {
  return (
    <div className={cn("relative", className)}>
      <SearchIcon className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
      <input
        type="search"
        placeholder={placeholder}
        className="h-10 w-full rounded-md border border-input bg-background pl-9 pr-3 text-sm outline-none transition placeholder:text-muted-foreground focus:border-ring focus:ring-2 focus:ring-ring/30"
        {...props}
      />
    </div>
  );
}
