import { cn } from "@/lib/utils";

interface AuthBrandProps {
  className?: string;
  inverse?: boolean;
}

export function AuthBrand({ className, inverse = false }: AuthBrandProps) {
  return (
    <div className={cn("flex items-center gap-3", className)}>
      <span
        aria-hidden="true"
        className="flex size-10 items-center justify-center rounded-xl bg-primary text-lg font-bold text-primary-foreground shadow-[0_8px_20px_-10px_rgba(250,204,21,0.85)]"
      >
        A
      </span>
      <span
        className={cn(
          "text-xl font-bold tracking-[-0.05em]",
          inverse ? "text-background" : "text-foreground",
        )}
      >
        AntreIn
      </span>
    </div>
  );
}
