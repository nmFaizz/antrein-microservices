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
        today: "font-bold text-primary",
        selected:
          "bg-primary text-primary-foreground rounded-md hover:bg-primary",
        day: "rounded-md hover:bg-accent",
        chevron: "fill-current",
        ...classNames,
      }}
      {...props}
    />
  );
}
