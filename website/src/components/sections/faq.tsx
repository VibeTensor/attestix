"use client";

import { useState } from "react";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { siteConfig } from "@/lib/config";

export function FAQ() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <>
      <section className="bg-atx-bg px-6 pb-16 pt-16 text-center md:pt-20">
        <div className="mx-auto max-w-[860px]">
          <AtxEyebrow>Frequently asked</AtxEyebrow>
          <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
            Questions about <span className="text-atx-accent">Attestix.</span>
          </h1>
          <p className="mx-auto mt-5 max-w-[640px] text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
            Common questions from engineers, compliance leads, and legal teams
            evaluating Attestix for production use. If you cannot find what you
            are looking for, reach out on GitHub or email
            info@vibetensor.com.
          </p>
        </div>
      </section>

      <section className="bg-atx-bg-elev px-6 py-20">
        <div className="mx-auto max-w-[720px] rounded-xl border border-atx-line bg-atx-panel/60 px-6">
          {siteConfig.faq.map((item, i) => {
            const isOpen = open === i;
            return (
              <div
                key={i}
                className={i ? "border-t border-atx-line-soft" : undefined}
              >
                <button
                  type="button"
                  aria-expanded={isOpen}
                  onClick={() => setOpen(isOpen ? null : i)}
                  className="flex w-full items-start gap-3 py-5 text-left text-[15px] font-medium text-atx-ink transition-colors duration-200 hover:text-atx-accent"
                >
                  <span
                    className={`text-atx-ink-dim transition-transform duration-200 ${
                      isOpen ? "rotate-90" : ""
                    }`}
                    aria-hidden
                  >
                    &rsaquo;
                  </span>
                  <span className="flex-1">{item.question}</span>
                </button>
                {isOpen && (
                  <div className="pb-5 pl-6 text-[15px] leading-[1.65] text-atx-ink-mid">
                    {item.answer}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>
    </>
  );
}
