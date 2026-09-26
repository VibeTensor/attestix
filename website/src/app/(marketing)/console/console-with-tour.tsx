"use client";

import { useState } from "react";
import { ConsoleTour } from "@/components/atx/console-tour";
import { ConsoleWorkspace } from "./console-workspace";

// The console demo plus its guided tour. autoStart: begin the tour on mount
// (used when a visitor explicitly enters the demo from the homepage).
export function ConsoleWithTour({ autoStart = false }: { autoStart?: boolean }) {
  const [root, setRoot] = useState<HTMLDivElement | null>(null);
  const [touring, setTouring] = useState(autoStart);

  return (
    <div ref={setRoot} className="relative">
      {!touring && (
        <button
          type="button"
          onClick={() => setTouring(true)}
          className="mb-3 inline-flex items-center gap-2 rounded-full border border-atx-line px-4 py-1.5 text-[13px] font-medium text-atx-ink-mid transition-colors duration-200 hover:border-atx-ink-dim hover:text-atx-ink"
        >
          Take the 1-minute tour
        </button>
      )}
      <ConsoleWorkspace />
      {touring && root && <ConsoleTour root={root} onDone={() => setTouring(false)} />}
    </div>
  );
}
