"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const STORAGE_KEY = "atx-console-banner-dismissed-v1";

export function ConsoleBanner() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    try {
      if (!window.localStorage.getItem(STORAGE_KEY)) setShow(true);
    } catch {
      // ignore
    }
  }, []);

  if (!show) return null;

  const dismiss = () => {
    try {
      window.localStorage.setItem(STORAGE_KEY, "1");
    } catch {
      // ignore
    }
    setShow(false);
  };

  return (
    <div className="mb-6 flex flex-col gap-3 rounded-atx-md border border-atx-accent/40 bg-atx-accent-soft p-5 md:flex-row md:items-center">
      <div className="flex-1">
        <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-accent">
          Interactive preview
        </div>
        <p className="mt-1.5 text-[13.5px] leading-[1.55] text-atx-ink">
          Data below is simulated. All agent IDs, DIDs, hashes, credentials,
          and anchors are deterministic fixtures. Run{" "}
          <code className="rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-1.5 py-0.5 font-mono-atx text-[12px] text-atx-accent">
            pip install attestix
          </code>{" "}
          for a working install.
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <Link
          href="/docs/getting-started"
          className="inline-flex h-8 items-center rounded-atx-sm border border-atx-line px-3 font-mono-atx text-[11.5px] text-atx-ink hover:border-atx-ink-dim"
        >
          Install guide
        </Link>
        <Link
          href="/demo-call"
          className="inline-flex h-8 items-center rounded-atx-sm border border-atx-line px-3 font-mono-atx text-[11.5px] text-atx-ink hover:border-atx-ink-dim"
        >
          Book a demo
        </Link>
        <button
          type="button"
          onClick={dismiss}
          aria-label="Dismiss banner"
          className="inline-flex h-8 items-center rounded-atx-sm bg-atx-accent px-3 font-mono-atx text-[11.5px] font-medium text-[oklch(0.14_0.01_180)] hover:bg-atx-accent-deep"
        >
          Got it
        </button>
      </div>
    </div>
  );
}
