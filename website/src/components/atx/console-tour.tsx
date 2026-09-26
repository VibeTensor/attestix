"use client";

import Link from "next/link";
import { useCallback, useEffect, useLayoutEffect, useState } from "react";

// Guided tour of the console demo: dims the page, spotlights one element,
// and drives the real UI between steps (open an agent, switch tabs, go back).
// Targets are found inside `root` by selector or by visible text.

type Find = { selector: string } | { text: string; within?: string };

interface Step {
  body: string;
  target?: Find;
  /** Clicked before the step is shown (drives the demo UI). */
  before?: Find;
  button?: string;
  /** Click the target itself when the button is pressed. */
  clickTarget?: boolean;
  cta?: { label: string; href: string };
}

const STEPS: Step[] = [
  {
    target: { selector: '[aria-label^="Open "]' },
    body: "Every agent in your fleet has a verifiable identity. Let's open this one.",
    button: "Show me",
    clickTarget: true,
  },
  {
    target: { selector: '[data-tour="identity"]' },
    body: "Its identity: a DID and a signed record, issued before the agent's first action.",
  },
  {
    before: { text: "compliance", within: '[data-tour="tabs"] button' },
    target: { selector: '[data-tour="tab-body"]' },
    body: "Its EU AI Act risk profile and Article 43 conformity route are recorded with the identity.",
  },
  {
    before: { text: "Audit trail", within: '[data-tour="tabs"] button' },
    target: { selector: '[data-tour="tab-body"]' },
    body: "Every action the agent takes lands in a hash-chained audit trail. Each entry commits to the one before it, so any edit breaks the chain.",
  },
  {
    before: { text: "credentials", within: '[data-tour="tabs"] button' },
    target: { selector: '[data-tour="tab-body"]' },
    body: "Credentials issued to this agent. Anyone can check the signature offline, without calling Attestix.",
  },
  {
    before: { text: "back to agents", within: "button" },
    target: { selector: "table" },
    body: "That was one agent. Here is the whole fleet: risk tiers, compliance status, and trust scores at a glance.",
  },
  {
    body: "Want verifiable identity and audit records for your own agents? Attestix is open source.",
    button: "Close",
    cta: { label: "Get started", href: "/docs/getting-started" },
  },
];

function find(root: HTMLElement, f?: Find): HTMLElement | null {
  if (!f) return null;
  if ("selector" in f) return root.querySelector<HTMLElement>(f.selector);
  const want = f.text.toLowerCase();
  return (
    [...root.querySelectorAll<HTMLElement>(f.within ?? "*")].find(
      (e) => e.innerText?.trim().toLowerCase() === want ||
             e.innerText?.trim().toLowerCase().endsWith(want),
    ) ?? null
  );
}

export function ConsoleTour({ root, onDone }: { root: HTMLElement | null; onDone: () => void }) {
  const [i, setI] = useState(0);
  const [rect, setRect] = useState<DOMRect | null>(null);
  const step = STEPS[i];

  const measure = useCallback(() => {
    const el = root ? find(root, step.target) : null;
    setRect(el ? el.getBoundingClientRect() : null);
  }, [root, step]);

  // run the step's UI action, then bring the target into view and measure
  useLayoutEffect(() => {
    if (!root) return;
    find(root, step.before)?.click();
    const t = window.setTimeout(() => {
      find(root, step.target)?.scrollIntoView({ block: "center", behavior: "smooth" });
      window.setTimeout(measure, 350);
    }, 120);
    return () => window.clearTimeout(t);
  }, [root, step, measure]);

  useEffect(() => {
    window.addEventListener("resize", measure);
    window.addEventListener("scroll", measure, true);
    const esc = (e: KeyboardEvent) => e.key === "Escape" && onDone();
    window.addEventListener("keydown", esc);
    return () => {
      window.removeEventListener("resize", measure);
      window.removeEventListener("scroll", measure, true);
      window.removeEventListener("keydown", esc);
    };
  }, [measure, onDone]);

  const next = () => {
    if (step.clickTarget && root) find(root, step.target)?.click();
    if (i + 1 < STEPS.length) setI(i + 1);
    else onDone();
  };

  // Place the card where it does not cover the target: right, left, below,
  // above; if the target fills the screen, pin to the bottom-right corner.
  const W = 320, H = 200, G = 16;
  let pos: React.CSSProperties = { left: "50%", top: "50%", transform: "translate(-50%, -50%)" };
  if (rect) {
    const vw = window.innerWidth, vh = window.innerHeight;
    const topAligned = Math.max(G, Math.min(rect.top, vh - H - G));
    const leftAligned = Math.max(G, Math.min(rect.left, vw - W - G));
    if (rect.right + G + W < vw) pos = { left: rect.right + G, top: topAligned };
    else if (rect.left - G - W > 0) pos = { left: rect.left - G - W, top: topAligned };
    else if (rect.bottom + G + H < vh) pos = { left: leftAligned, top: rect.bottom + G };
    else if (rect.top - G - H > 0) pos = { left: leftAligned, top: rect.top - G - H };
    else pos = { right: G + 8, bottom: G + 8 };
  }

  return (
    <div className="fixed inset-0 z-[60]" role="dialog" aria-modal="true" aria-label="Console tour">
      {rect ? (
        <div
          aria-hidden
          className="pointer-events-none fixed rounded-xl ring-2 ring-[#A7CFFF] transition-all duration-300"
          style={{
            left: rect.left - 6, top: rect.top - 6, width: rect.width + 12, height: rect.height + 12,
            boxShadow: "0 0 0 9999px rgba(4, 8, 8, 0.62)",
          }}
        />
      ) : (
        <div aria-hidden className="fixed inset-0 bg-[rgba(4,8,8,0.62)]" />
      )}
      <div
        className="fixed rounded-xl border border-[#A7CFFF]/70 bg-[#17222e] p-5 shadow-[0_12px_40px_rgba(0,0,0,0.5)] transition-all duration-300"
        style={{ width: W, ...pos }}
      >
        <p className="text-[12px] font-semibold text-[#A7CFFF]">
          Step {i + 1} of {STEPS.length}
        </p>
        <p className="mt-2 text-[15px] font-medium leading-[1.5] text-white">{step.body}</p>
        <div className="mt-4 flex items-center justify-between gap-3">
          <button type="button" onClick={onDone} className="text-[12px] text-white/50 hover:text-white/80">
            Skip tour
          </button>
          <div className="flex gap-2">
            {step.cta && (
              <Link
                href={step.cta.href}
                className="rounded-lg bg-atx-accent px-3.5 py-2 text-[13px] font-medium text-[oklch(0.14_0.01_180)]"
              >
                {step.cta.label}
              </Link>
            )}
            <button
              type="button"
              onClick={next}
              autoFocus
              className="rounded-lg bg-[#A7CFFF] px-3.5 py-2 text-[13px] font-medium text-[#0d1620] hover:bg-[#c3ddff]"
            >
              {step.button ?? "Next"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
