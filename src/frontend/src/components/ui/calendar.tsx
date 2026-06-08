"use client";

import { DayPicker, type DayPickerProps } from "react-day-picker";
import "react-day-picker/style.css";

import { cn } from "@/lib/utils";

/**
 * Thin wrapper over `react-day-picker`'s `DayPicker`, styled with Tailwind.
 * Used standalone or inside `<DatePicker>`.
 */
export function Calendar({ className, classNames, ...props }: DayPickerProps) {
  return (
    <DayPicker
      className={cn("p-3", className)}
      classNames={{
        today: "font-bold text-foreground",
        selected:
          "bg-foreground text-background rounded-md hover:bg-foreground",
        chevron: "fill-current",
        ...classNames,
      }}
      {...props}
    />
  );
}
