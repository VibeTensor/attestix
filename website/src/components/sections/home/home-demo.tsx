"use client";

import Link from "next/link";
import { useState } from "react";
import { ConsoleWorkspace } from "@/app/(marketing)/console/console-workspace";
import { PreviewCard } from "@/components/sections/v2/console-preview";

// Blurred product preview that expands in place into the live (simulated)
// console. Same motion curve as the pattern it adapts: .45s ease-out-expo.
export function HomeDemo() {
  const [open, setOpen] = useState(false);

  return (
    <section id="demo" className="px-6 pb-14">
      <div
        className="relative mx-auto overflow-hidden rounded-2xl border border-atx-line bg-atx-bg-sunken shadow-[0_24px_80px_-24px_rgba(0,0,0,0.7)] transition-[max-width] duration-[450ms] ease-[cubic-bezier(0.2,0.7,0.2,1)]"
        style={{ maxWidth: open ? 1200 : 840 }}
      >
        {open ? (
          <div className="max-h-[78vh] overflow-auto px-4 pb-4 pt-14 md:px-6 md:pb-6">
            <ConsoleWorkspace />
          </div>
        ) : (
          <>
            <div aria-hidden className="pointer-events-none select-none opacity-70 blur-[2px]">
              <PreviewCard />
            </div>
            <div className="absolute inset-0 grid place-items-center">
              <button
                type="button"
                onClick={() => setOpen(true)}
                className="rounded-full bg-white px-7 py-3.5 text-[15px] font-medium text-[#111315] shadow-[0_8px_30px_rgba(0,0,0,0.45)] transition-shadow duration-200 hover:shadow-[0_8px_40px_rgba(230,172,61,0.35)]"
              >
                Enter the console demo
              </button>
            </div>
          </>
        )}

        <div className="absolute right-2.5 top-2.5 z-10 flex gap-2">
          {open && (
            <button
              type="button"
              onClick={() => setOpen(false)}
              aria-label="Collapse demo"
              className="grid h-[34px] w-[34px] place-items-center rounded-full border border-atx-ink-dim bg-atx-panel text-[15px] text-atx-ink"
            >
              &times;
            </button>
          )}
          <Link
            href="/console"
            aria-label="Open the console demo in full page"
            className="grid h-[34px] w-[34px] place-items-center rounded-full border border-atx-ink-dim bg-atx-panel text-[15px] text-atx-ink"
          >
            &#8599;
          </Link>
        </div>
      </div>
      <p className="mt-4 text-center text-[13px] text-atx-ink-dim">
        Interactive preview. Data is simulated;{" "}
        <code className="font-mono-atx text-atx-accent">pip install attestix</code> for the real thing.
      </p>
    </section>
  );
}
