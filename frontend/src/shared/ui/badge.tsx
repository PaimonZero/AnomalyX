import type { HTMLAttributes, PropsWithChildren } from "react";

type BadgeTone = "neutral" | "info" | "success" | "warning" | "high" | "critical" | "accent";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: BadgeTone;
}

export function Badge({ children, className = "", tone = "neutral", ...props }: PropsWithChildren<BadgeProps>) {
  return (
    <span className={`badge badge--${tone} ${className}`.trim()} {...props}>
      {children}
    </span>
  );
}

