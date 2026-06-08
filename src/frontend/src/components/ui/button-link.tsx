import Link from "next/link";
import type { ComponentProps } from "react";

import {
  type ButtonSize,
  type ButtonVariant,
  buttonStyles,
} from "@/components/ui/button";

interface ButtonLinkProps extends ComponentProps<typeof Link> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}

/** A Next `Link` styled identically to `Button`. For navigation actions. */
export function ButtonLink({
  variant = "primary",
  size = "md",
  className,
  ...props
}: ButtonLinkProps) {
  return <Link className={buttonStyles(variant, size, className)} {...props} />;
}
