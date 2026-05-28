"use client";

import { useState } from "react";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { ATX_FRAMEWORKS } from "@/lib/atx-frameworks";

export function FrameworksSection() {
  const [active, setActive] = useState(ATX_FRAMEWORKS[0].slug);
  const f = ATX_FRAMEWORKS.find((x) => x.slug === active) ?? ATX_FRAMEWORKS[0];

  return (
    <section id="frameworks" className="border-t border-atx-line-soft py-24">
      <div className="mx-auto max-w-[1320px] px-7">
        <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
          <div>
            <AtxEyebrow number="06">Framework integrations</AtxEyebrow>
            <h2 className="mt-3 font-serif text-[clamp(28px,3.2vw,40px)] leading-[1.15] tracking-[-0.01em] text-atx-ink">
              Drop into your
              <br />
              <em className="italic text-atx-accent">agent stack.</em>
            </h2>
          </div>
          <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
            Three production integrations shipped in v0.3.0: LangChain, OpenAI
            Agents SDK, CrewAI. Four more documented as example integrations
            via the MCP protocol: Dify, Google ADK, Semantic Kernel, Strands.
          </p>
        </div>

        <div className="mt-14 overflow-hidden rounded-atx-md border border-atx-line-soft bg-atx-panel">
          <div
            role="tablist"
            aria-label="Framework integrations"
            className="grid grid-cols-3 border-b border-atx-line-soft sm:grid-cols-4 lg:grid-cols-7"
          >
            {ATX_FRAMEWORKS.map((x, i) => {
              const isActive = x.slug === active;
              return (
                <button
                  key={x.slug}
                  role="tab"
                  aria-selected={isActive}
                  onClick={() => setActive(x.slug)}
                  className={`flex flex-col items-start gap-1 border-atx-line-soft px-4 py-3 text-left transition-colors ${
                    i < ATX_FRAMEWORKS.length - 1 ? "border-r" : ""
                  } ${
                    isActive
                      ? "bg-atx-bg text-atx-ink"
                      : "bg-atx-bg-sunken text-atx-ink-dim hover:bg-atx-panel-hi hover:text-atx-ink-mid"
                  }`}
                >
                  <span
                    className={`font-mono-atx text-[10px] uppercase tracking-[0.12em] ${
                      x.status === "production"
                        ? "text-atx-accent"
                        : "text-atx-ink-faint"
                    }`}
                  >
                    {x.status === "production" ? "PROD" : "EXAMPLE"}
                  </span>
                  <span className="text-[12.5px] leading-tight">
                    {x.name}
                  </span>
                </button>
              );
            })}
          </div>

          <div className="grid gap-0 lg:grid-cols-[1fr_1.3fr]">
            <div className="border-atx-line-soft p-8 lg:border-r">
              <div className="flex items-center gap-2 font-mono-atx text-[10.5px] uppercase tracking-[0.14em]">
                <span
                  className={
                    f.status === "production"
                      ? "text-atx-accent"
                      : "text-atx-ink-faint"
                  }
                >
                  {f.status === "production"
                    ? "Real integration"
                    : "Example integration"}
                </span>
              </div>
              <h3 className="mt-4 font-serif text-[26px] leading-tight text-atx-ink">
                {f.name}
              </h3>
              <p className="mt-3 text-[14px] leading-[1.65] text-atx-ink-mid">
                {f.tagline}
              </p>
              <code className="mt-5 inline-block rounded-atx-sm border border-atx-line-soft bg-atx-bg-sunken px-3 py-2 font-mono-atx text-[12px] text-atx-ink-dim">
                <span className="text-atx-accent">$</span> {f.install}
              </code>
              <ul className="mt-5 space-y-2">
                {f.wires.map((w) => (
                  <li
                    key={w}
                    className="flex gap-3 text-[13px] leading-[1.55] text-atx-ink-mid"
                  >
                    <span className="mt-2 block h-1 w-1 shrink-0 rounded-full bg-atx-accent" />
                    {w}
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
                <span>example / {f.slug}.py</span>
                <span className="ml-auto text-atx-ok">&bull; ready</span>
              </div>
              <pre
                className="atx-code overflow-x-auto px-5 py-5 font-mono-atx text-[12.5px] leading-[1.6] text-atx-ink"
                dangerouslySetInnerHTML={{ __html: f.code }}
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
