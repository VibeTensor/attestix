"use client";

import { useState } from "react";
import { ATX_WORKFLOW } from "@/lib/atx-data";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";

export function WorkflowSection() {
  const [step, setStep] = useState(0);
  const w = ATX_WORKFLOW[step];

  return (
    <section
      id="workflow"
      className="border-t border-atx-line-soft py-24"
    >
      <div className="mx-auto max-w-[1320px] px-7">
        <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
          <div>
            <AtxEyebrow number="03">Seven steps</AtxEyebrow>
            <h2 className="mt-3 font-serif text-[clamp(28px,3.2vw,40px)] leading-[1.15] tracking-[-0.01em] text-atx-ink">
              From zero to
              <br />
              EU AI Act-compliant.
            </h2>
          </div>
          <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
            A high-risk AI agent, walked through the seven-step pipeline that
            produces a regulator-ready Declaration of Conformity. Each stage
            below maps to the EU AI Act article it satisfies, and the exact
            Attestix call that produces the artefact.
          </p>
        </div>

        <div className="mt-14 overflow-hidden rounded-atx-md border border-atx-line-soft bg-atx-panel">
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
                  className={`flex flex-col items-start gap-1 border-atx-line-soft px-4 py-3 text-left transition-colors [&:not(:last-child)]:border-r ${
                    active
                      ? "bg-atx-bg text-atx-ink"
                      : "bg-atx-bg-sunken text-atx-ink-dim hover:bg-atx-panel-hi hover:text-atx-ink-mid"
                  }`}
                >
                  <span
                    className={`font-mono-atx text-[10.5px] uppercase tracking-[0.12em] ${
                      active ? "text-atx-accent" : "text-atx-ink-faint"
                    }`}
                  >
                    STEP {s.n}
                  </span>
                  <span className="text-[12.5px] leading-tight">
                    {s.title}
                  </span>
                </button>
              );
            })}
          </div>

          <div className="grid gap-0 lg:grid-cols-[1fr_1.3fr]">
            <div className="border-atx-line-soft p-8 lg:border-r">
              <span className="inline-block rounded-atx-xs border border-atx-accent/40 bg-atx-accent-soft px-2 py-1 font-mono-atx text-[10.5px] uppercase tracking-[0.12em] text-atx-accent">
                {w.article}
              </span>
              <h3 className="mt-5 font-serif text-[26px] leading-tight text-atx-ink">
                {w.title}
              </h3>
              <p className="mt-3 text-[14px] leading-[1.65] text-atx-ink-mid">
                {w.desc}
              </p>
              <ul className="mt-5 space-y-2">
                {w.bullets.map((b) => (
                  <li
                    key={b}
                    className="flex gap-3 text-[13px] leading-[1.55] text-atx-ink-mid"
                  >
                    <span className="mt-2 block h-1 w-1 shrink-0 rounded-full bg-atx-accent" />
                    {b}
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-atx-bg-sunken">
              <div className="flex items-center gap-3 border-b border-atx-line-soft px-4 py-2.5 font-mono-atx text-[11px] text-atx-ink-dim">
                <span className="flex gap-1.5">
                  <span className="inline-block h-2 w-2 rounded-full bg-atx-err/60" />
                  <span className="inline-block h-2 w-2 rounded-full bg-atx-warn/60" />
                  <span className="inline-block h-2 w-2 rounded-full bg-atx-ok/60" />
                </span>
                <span>python / attestix.quickstart.py</span>
                <span className="ml-auto text-atx-ok">&bull; running</span>
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
                  className={`h-1 w-6 rounded-full ${
                    i <= step ? "bg-atx-accent" : "bg-atx-line-soft"
                  }`}
                />
              ))}
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={step === 0}
                onClick={() => setStep(Math.max(0, step - 1))}
                className="inline-flex h-8 items-center rounded-atx-sm border border-atx-line px-3 text-[12px] text-atx-ink disabled:opacity-40"
              >
                &lsaquo; prev
              </button>
              <button
                type="button"
                disabled={step === ATX_WORKFLOW.length - 1}
                onClick={() =>
                  setStep(Math.min(ATX_WORKFLOW.length - 1, step + 1))
                }
                className="inline-flex h-8 items-center rounded-atx-sm bg-atx-accent px-3 text-[12px] font-medium text-[oklch(0.14_0.01_180)] hover:bg-atx-accent-deep disabled:opacity-40"
              >
                next &rsaquo;
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
