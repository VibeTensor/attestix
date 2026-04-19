"use client";

import { useState } from "react";

const DEFAULT_PUBLICATION =
  process.env.NEXT_PUBLIC_SUBSTACK_URL || "https://vibetensor.substack.com";

export function AtxSubstackSubscribe() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "ok" | "err">(
    "idle"
  );
  const [message, setMessage] = useState("");

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const trimmed = email.trim();
    if (!trimmed || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
      setStatus("err");
      setMessage("Please enter a valid email.");
      return;
    }
    setStatus("submitting");
    const target = `${DEFAULT_PUBLICATION}/subscribe?email=${encodeURIComponent(trimmed)}`;
    try {
      const handle = window.open(target, "_blank", "noopener,noreferrer");
      if (!handle) {
        setStatus("err");
        setMessage(
          "Popup blocked. Please allow popups or open the Substack link directly."
        );
        return;
      }
      setStatus("ok");
      setMessage("Opened Substack in a new tab to confirm your email.");
    } catch {
      setStatus("err");
      setMessage("Could not open subscribe window.");
    }
  };

  return (
    <form
      onSubmit={onSubmit}
      className="rounded-atx-md border border-atx-line-soft bg-atx-panel p-6"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
            Newsletter
          </div>
          <h2 className="mt-1 font-serif text-[22px] leading-tight text-atx-ink">
            Subscribe via Substack
          </h2>
          <p className="mt-1 max-w-[520px] text-[13px] leading-[1.55] text-atx-ink-mid">
            Release notes, research summaries, and field reports. One email
            per post, no spam. Hosted on Substack.
          </p>
        </div>
        <a
          href={DEFAULT_PUBLICATION}
          target="_blank"
          rel="noopener noreferrer"
          className="font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-accent hover:underline"
        >
          View on Substack &rarr;
        </a>
      </div>

      <div className="mt-5 flex flex-col gap-2 sm:flex-row">
        <label htmlFor="atx-sub-email" className="sr-only">
          Email address
        </label>
        <input
          id="atx-sub-email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@company.com"
          className="h-10 flex-1 rounded-atx-sm border border-atx-line bg-atx-bg-sunken px-3 font-mono-atx text-[13px] text-atx-ink outline-none focus:border-atx-accent"
        />
        <button
          type="submit"
          disabled={status === "submitting"}
          className="inline-flex h-10 items-center justify-center rounded-atx-sm bg-atx-accent px-5 font-mono-atx text-[12px] font-medium text-[oklch(0.14_0.01_180)] hover:bg-atx-accent-deep disabled:opacity-60"
        >
          {status === "submitting" ? "Opening..." : "Subscribe \u2192"}
        </button>
      </div>

      {status === "ok" && (
        <div className="mt-3 font-mono-atx text-[11.5px] text-atx-ok">
          &#10003; {message}
        </div>
      )}
      {status === "err" && (
        <div className="mt-3 font-mono-atx text-[11.5px] text-atx-err">
          &#x2717; {message}
        </div>
      )}
    </form>
  );
}
