import { cn } from "@/lib/utils";

interface AtxEyebrowProps {
  /** Accepted for compatibility; sections are no longer numbered. */
  number?: string;
  children: React.ReactNode;
  accent?: boolean;
  className?: string;
}

// Small sentence-case label above a heading, in the accent colour.
export function AtxEyebrow({ children, accent = true, className }: AtxEyebrowProps) {
  return (
    <div
      className={cn(
        "text-[14px] font-medium",
        accent ? "text-atx-accent" : "text-atx-ink-mid",
        className
      )}
    >
      {children}
    </div>
  );
}
