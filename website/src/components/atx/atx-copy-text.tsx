"use client";

import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

interface AtxCopyTextProps {
  value: string;
  children?: React.ReactNode;
  className?: string;
  title?: string;
}

export function AtxCopyText({
  value,
  children,
  className,
  title,
}: AtxCopyTextProps) {
  const [copied, setCopied] = useState(false);
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) window.clearTimeout(timerRef.current);
    };
  }, []);

  const handleClick = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      if (timerRef.current) window.clearTimeout(timerRef.current);
      timerRef.current = window.setTimeout(() => setCopied(false), 900);
    } catch {
      // clipboard blocked; swallow silently
    }
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      title={title ?? "Copy"}
      aria-label={title ?? "Copy"}
      className={cn(
        "cursor-pointer text-left font-mono-atx",
        copied && "text-atx-ok",
        className
      )}
    >
      {copied ? "copied \u2713" : children ?? value}
    </button>
  );
}
