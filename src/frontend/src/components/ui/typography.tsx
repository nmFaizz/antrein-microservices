import { cn } from "@/lib/utils";

type HeadingProps = React.HTMLAttributes<HTMLHeadingElement>;
type ParagraphProps = React.HTMLAttributes<HTMLParagraphElement>;

export function H1({ className, ...props }: HeadingProps) {
  return (
    <h1
      className={cn("text-3xl font-bold tracking-tight", className)}
      {...props}
    />
  );
}

export function H2({ className, ...props }: HeadingProps) {
  return (
    <h2
      className={cn("text-2xl font-semibold tracking-tight", className)}
      {...props}
    />
  );
}

export function H3({ className, ...props }: HeadingProps) {
  return <h3 className={cn("text-xl font-semibold", className)} {...props} />;
}

export function H4({ className, ...props }: HeadingProps) {
  return <h4 className={cn("text-lg font-semibold", className)} {...props} />;
}

export function P({ className, ...props }: ParagraphProps) {
  return <p className={cn("text-sm leading-6", className)} {...props} />;
}

export function Lead({ className, ...props }: ParagraphProps) {
  return (
    <p className={cn("text-lg text-muted-foreground", className)} {...props} />
  );
}

export function Muted({ className, ...props }: ParagraphProps) {
  return (
    <p className={cn("text-sm text-muted-foreground", className)} {...props} />
  );
}

export function Small({ className, ...props }: ParagraphProps) {
  return <p className={cn("text-xs font-medium", className)} {...props} />;
}
