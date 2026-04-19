"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const STORAGE_KEY = "atx-cookie-consent-v1";

export function AtxCookieConsent() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    try {
      if (!window.localStorage.getItem(STORAGE_KEY)) setShow(true);
    } catch {
      // localStorage unavailable; do not show
    }
  }, []);

  const dismiss = (choice: "accept" | "decline") => {
    try {
      window.localStorage.setItem(STORAGE_KEY, choice);
    } catch {
      // ignore
    }
    setShow(false);
  };

  if (!show) return null;

  return (
    <div
      role="region"
      aria-label="Cookie notice"
      className="fixed inset-x-4 bottom-4 z-[90] mx-auto max-w-[720px] rounded-atx-md border border-atx-line bg-atx-panel/95 p-5 shadow-[var(--atx-shadow-md)] backdrop-blur-md"
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start">
        <div className="flex-1 text-[13px] leading-[1.6] text-atx-ink-mid">
          We use cookies only for essential site function. No third-party
          analytics or ad trackers. See our{" "}
          <Link
            href="/legal/cookies"
            className="text-atx-accent hover:underline"
          >
            cookie policy
          </Link>
          .
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => dismiss("decline")}
            className="inline-flex h-8 items-center rounded-atx-sm border border-atx-line px-3 font-mono-atx text-[11.5px] text-atx-ink transition-colors hover:border-atx-ink-dim"
          >
            Decline
          </button>
          <button
            type="button"
            onClick={() => dismiss("accept")}
            className="inline-flex h-8 items-center rounded-atx-sm bg-atx-accent px-3 font-mono-atx text-[11.5px] font-medium text-[oklch(0.14_0.01_180)] hover:bg-atx-accent-deep"
          >
            Accept
          </button>
        </div>
      </div>
    </div>
  );
}
