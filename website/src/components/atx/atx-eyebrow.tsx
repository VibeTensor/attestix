import { cn } from "@/lib/utils";

interface AtxEyebrowProps {
  number?: string;
  children: React.ReactNode;
  accent?: boolean;
  className?: string;
}

export function AtxEyebrow({
  number,
  children,
  accent,
  className,
}: AtxEyebrowProps) {
  return (
    <div
      className={cn(
        "font-mono-atx text-[11px] font-medium tracking-[0.14em] uppercase",
        accent ? "text-atx-accent" : "text-atx-ink-dim",
        className
      )}
    >
      {number ? `\u00A7 ${number} / ` : null}
      {children}
    </div>
  );
}
