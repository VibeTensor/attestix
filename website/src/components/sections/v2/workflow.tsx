"use client";

import { useState } from "react";
import { ATX_WORKFLOW } from "@/lib/atx-data";

const WRAP = "mx-auto w-full max-w-[1200px] px-6";
const H2 = "text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink";
const LEAD = "text-[17.5px] leading-[1.6] text-atx-ink-mid";

export function WorkflowSection() {
  const [step, setStep] = useState(0);
  const w = ATX_WORKFLOW[step];

  return (
    <section id="workflow" className="scroll-mt-20 bg-atx-bg py-20">
      <div className={WRAP}>
        <div className="text-center">
          <h2 className={H2}>
            From zero to <span className="text-atx-accent">signed EU AI Act evidence</span>
          </h2>
          <p className={`mx-auto mt-4 max-w-[760px] ${LEAD}`}>
            A high-risk AI agent, walked through the seven-step pipeline that
            produces a signed Annex V Declaration of Conformity. Each stage
            below names the EU AI Act article it records evidence for, and the
            exact Attestix call that produces the artefact.
          </p>
        </div>

        <div className="mt-12 overflow-hidden rounded-2xl border border-atx-line bg-atx-panel/60">
          <div
            role="tablist"
            aria-label="Compliance workflow steps"
            className="grid grid-cols-2 border-b border-atx-line-soft sm:grid-cols-4 lg:grid-cols-7"
          >
            {ATX_WORKFLOW.map((s, i) => {
              const active = step === i;
              return (
                <button
                  key={s.n}
                  role="tab"
                  aria-selected={active}
                  onClick={() => setStep(i)}
                  className={`flex flex-col items-start gap-1 border-atx-line-soft px-4 py-3.5 text-left transition-colors duration-200 [&:not(:last-child)]:border-r ${
                    active
                      ? "bg-atx-accent/[0.08] text-atx-ink"
                      : "bg-atx-bg-sunken/60 text-atx-ink-dim hover:text-atx-ink-mid"
                  }`}
                >
                  <span className={`text-[13px] font-medium ${active ? "text-atx-accent" : "text-atx-ink-dim"}`}>
                    Step {s.n}
                  </span>
                  <span className="text-[13.5px] leading-tight">{s.title}</span>
                </button>
              );
            })}
          </div>

          <div className="grid gap-0 lg:grid-cols-[1fr_1.3fr]">
            <div className="border-atx-line-soft p-7 lg:border-r">
              <span className="inline-block rounded-full bg-atx-accent/15 px-3 py-1 text-[13px] font-medium text-atx-accent">
                {w.article}
              </span>
              <h3 className="mt-4 text-[21px] font-semibold leading-[1.25] tracking-[-0.48px] text-atx-ink">
                {w.title}
              </h3>
              <p className="mt-3 text-[15px] leading-[1.6] text-atx-ink-mid">{w.desc}</p>
              <ul className="mt-5 space-y-2">
                {w.bullets.map((b) => (
                  <li key={b} className="flex gap-3 text-[14px] leading-[1.55] text-atx-ink-mid">
                    <span className="mt-2 block h-1.5 w-1.5 shrink-0 rounded-full bg-atx-accent" />
                    {b}
                  </li>
                ))}
              </ul>
            </div>

            <div className="min-w-0 bg-atx-bg-sunken">
              <div className="flex items-center gap-3 border-b border-atx-line-soft px-4 py-2.5 text-[12px] text-atx-ink-dim">
                <span className="flex gap-1.5">
                  <span className="inline-block h-2 w-2 rounded-full bg-atx-err/60" />
                  <span className="inline-block h-2 w-2 rounded-full bg-atx-warn/60" />
                  <span className="inline-block h-2 w-2 rounded-full bg-atx-ok/60" />
                </span>
                <span className="font-mono-atx">python / attestix.quickstart.py</span>
                <span className="ml-auto text-atx-ok">Running</span>
              </div>
              <pre
                className="atx-code overflow-x-auto px-5 py-5 font-mono-atx text-[12.5px] leading-[1.6] text-atx-ink"
                dangerouslySetInnerHTML={{ __html: w.code }}
              />
            </div>
          </div>

          <div className="flex items-center justify-between border-t border-atx-line-soft px-5 py-3">
            <div className="flex gap-1.5">
              {ATX_WORKFLOW.map((_, i) => (
                <span
                  key={i}
                  className={`h-1 w-6 rounded-full ${i <= step ? "bg-atx-accent" : "bg-atx-line-soft"}`}
                />
              ))}
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={step === 0}
                onClick={() => setStep(Math.max(0, step - 1))}
                className="inline-flex h-9 items-center rounded-full border border-atx-line px-4 text-[13px] font-medium text-atx-ink-mid transition-colors duration-200 hover:border-atx-ink-dim hover:text-atx-ink disabled:opacity-40"
              >
                Prev
              </button>
              <button
                type="button"
                disabled={step === ATX_WORKFLOW.length - 1}
                onClick={() => setStep(Math.min(ATX_WORKFLOW.length - 1, step + 1))}
                className="inline-flex h-9 items-center rounded-full bg-atx-accent px-4 text-[13px] font-medium text-[oklch(0.14_0.01_180)] transition-colors duration-200 hover:bg-atx-accent-deep disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
