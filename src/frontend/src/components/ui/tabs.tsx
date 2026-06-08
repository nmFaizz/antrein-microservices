"use client";

import { createContext, useContext, useId, useState } from "react";

import { cn } from "@/lib/utils";

interface TabsContextValue {
  value: string;
  setValue: (value: string) => void;
  baseId: string;
}

const TabsContext = createContext<TabsContextValue | null>(null);

function useTabs(component: string) {
  const ctx = useContext(TabsContext);
  if (!ctx) throw new Error(`<${component}> must be used inside <Tabs>`);
  return ctx;
}

interface TabsProps {
  defaultValue: string;
  children: React.ReactNode;
  className?: string;
}

export function Tabs({ defaultValue, children, className }: TabsProps) {
  const [value, setValue] = useState(defaultValue);
  const baseId = useId();
  return (
    <TabsContext.Provider value={{ value, setValue, baseId }}>
      <div className={cn("flex flex-col gap-4", className)}>{children}</div>
    </TabsContext.Provider>
  );
}

export function TabList({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      role="tablist"
      className={cn(
        "inline-flex items-center gap-1 rounded-lg border border-border bg-muted p-1",
        className,
      )}
    >
      {children}
    </div>
  );
}

export function Tab({
  value,
  children,
}: {
  value: string;
  children: React.ReactNode;
}) {
  const ctx = useTabs("Tab");
  const active = ctx.value === value;
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      aria-controls={`${ctx.baseId}-panel-${value}`}
      id={`${ctx.baseId}-tab-${value}`}
      className={cn(
        "rounded-md px-3 py-1.5 text-sm font-medium transition",
        active
          ? "bg-card text-foreground shadow-sm"
          : "text-muted-foreground hover:text-foreground",
      )}
      onClick={() => ctx.setValue(value)}
    >
      {children}
    </button>
  );
}

export function TabPanel({
  value,
  children,
  className,
}: {
  value: string;
  children: React.ReactNode;
  className?: string;
}) {
  const ctx = useTabs("TabPanel");
  if (ctx.value !== value) return null;
  return (
    <div
      role="tabpanel"
      id={`${ctx.baseId}-panel-${value}`}
      aria-labelledby={`${ctx.baseId}-tab-${value}`}
      className={className}
    >
      {children}
    </div>
  );
}
