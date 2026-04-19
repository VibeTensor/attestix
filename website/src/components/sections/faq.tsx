"use client";

import { useState } from "react";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { siteConfig } from "@/lib/config";

export function FAQ() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section className="mx-auto max-w-[1320px] px-7 py-24">
      <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
        <div>
          <AtxEyebrow>Frequently asked</AtxEyebrow>
          <h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
            Questions about
            <br />
            <em className="italic text-atx-accent">Attestix.</em>
          </h1>
        </div>
        <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
          Common questions from engineers, compliance leads, and legal teams
          evaluating Attestix for production use. If you cannot find what you
          are looking for, reach out on GitHub or email
          info@vibetensor.com.
        </p>
      </div>

      <div className="mt-12 overflow-hidden rounded-atx-md border border-atx-line-soft bg-atx-panel">
        {siteConfig.faq.map((item, i) => {
          const isOpen = open === i;
          return (
            <div
              key={i}
              className="border-b border-atx-line-soft last:border-b-0"
            >
              <button
                type="button"
                aria-expanded={isOpen}
                onClick={() => setOpen(isOpen ? null : i)}
                className="flex w-full items-start gap-4 px-6 py-5 text-left transition-colors hover:bg-atx-panel-hi"
              >
                <span className="mt-1 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <span className="flex-1 font-serif text-[18px] leading-[1.35] text-atx-ink">
                  {item.question}
                </span>
                <span
                  className={`mt-1 font-mono-atx text-[14px] text-atx-accent transition-transform ${
                    isOpen ? "rotate-45" : ""
                  }`}
                  aria-hidden
                >
                  +
                </span>
              </button>
              {isOpen && (
                <div className="px-6 pb-6 pl-[72px] text-[14px] leading-[1.7] text-atx-ink-mid">
                  {item.answer}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
