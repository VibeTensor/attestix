"use client";

import { useState } from "react";
import { ATX_FRAMEWORKS } from "@/lib/atx-frameworks";

const WRAP = "mx-auto w-full max-w-[1200px] px-6";
const H2 = "text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink";
const LEAD = "text-[17.5px] leading-[1.6] text-atx-ink-mid";

export function FrameworksSection() {
  const [active, setActive] = useState(ATX_FRAMEWORKS[0].slug);
  const f = ATX_FRAMEWORKS.find((x) => x.slug === active) ?? ATX_FRAMEWORKS[0];
  const prod = f.status === "production";

  return (
    <section id="frameworks" className="scroll-mt-20 bg-atx-bg-elev py-20">
      <div className={WRAP}>
        <div className="text-center">
          <h2 className={H2}>
            Drop into your <span className="text-atx-accent">agent stack</span>
          </h2>
          <p className={`mx-auto mt-4 max-w-[760px] ${LEAD}`}>
            Three production integrations shipped in v0.3.0: LangChain, OpenAI
            Agents SDK, CrewAI. Four more documented as example integrations
            via the MCP protocol: Dify, Google ADK, Semantic Kernel, Strands.
          </p>
        </div>

        <div className="mt-12 overflow-hidden rounded-2xl border border-atx-line bg-atx-panel/60">
          <div
            role="tablist"
            aria-label="Framework integrations"
            className="grid grid-cols-2 border-b border-atx-line-soft sm:grid-cols-4 lg:grid-cols-7"
          >
            {ATX_FRAMEWORKS.map((x, i) => {
              const isActive = x.slug === active;
              return (
                <button
                  key={x.slug}
                  role="tab"
                  aria-selected={isActive}
                  onClick={() => setActive(x.slug)}
                  className={`flex flex-col items-start gap-1 border-atx-line-soft px-4 py-3.5 text-left transition-colors duration-200 ${
                    i < ATX_FRAMEWORKS.length - 1 ? "border-r" : ""
                  } ${
                    isActive
                      ? "bg-atx-accent/[0.08] text-atx-ink"
                      : "bg-atx-bg-sunken/60 text-atx-ink-dim hover:text-atx-ink-mid"
                  }`}
                >
                  <span
                    className={`text-[12.5px] font-medium ${
                      x.status === "production" ? "text-atx-accent" : "text-atx-ink-dim"
                    }`}
                  >
                    {x.status === "production" ? "Production" : "Example"}
                  </span>
                  <span className="text-[13.5px] leading-tight">{x.name}</span>
                </button>
              );
            })}
          </div>

          <div className="grid gap-0 lg:grid-cols-[1fr_1.3fr]">
            <div className="min-w-0 border-atx-line-soft p-7 lg:border-r">
              <span
                className={`inline-block rounded-full px-3 py-1 text-[13px] font-medium ${
                  prod ? "bg-atx-accent/15 text-atx-accent" : "bg-atx-info/15 text-atx-info"
                }`}
              >
                {prod ? "Real integration" : "Example integration"}
              </span>
              <h3 className="mt-4 text-[21px] font-semibold leading-[1.25] tracking-[-0.48px] text-atx-ink">
                {f.name}
              </h3>
              <p className="mt-3 text-[15px] leading-[1.6] text-atx-ink-mid">{f.tagline}</p>
              <code className="mt-5 inline-block max-w-full overflow-x-auto whitespace-nowrap rounded-xl border border-atx-line-soft bg-atx-bg-sunken px-3 py-2 font-mono-atx text-[12px] text-atx-ink-dim">
                <span className="text-atx-accent">$</span> {f.install}
              </code>
              <ul className="mt-5 space-y-2">
                {f.wires.map((w) => (
                  <li key={w} className="flex gap-3 text-[14px] leading-[1.55] text-atx-ink-mid">
                    <span className="mt-2 block h-1.5 w-1.5 shrink-0 rounded-full bg-atx-accent" />
                    {w}
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
                <span className="font-mono-atx">example / {f.slug}.py</span>
                <span className="ml-auto text-atx-ok">Ready</span>
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
