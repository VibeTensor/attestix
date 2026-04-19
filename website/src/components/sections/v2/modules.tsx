import { ATX_MODULES } from "@/lib/atx-data";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { AtxIcon } from "@/components/atx/atx-icons";

export function ModulesSection() {
  return (
    <section
      id="modules"
      className="border-t border-atx-line-soft py-24"
    >
      <div className="mx-auto max-w-[1320px] px-7">
        <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
          <div>
            <AtxEyebrow number="02">The stack</AtxEyebrow>
            <h2 className="mt-3 font-serif text-[clamp(28px,3.2vw,40px)] leading-[1.15] tracking-[-0.01em] text-atx-ink">
              Nine modules.
              <br />
              Forty-seven tools.
            </h2>
          </div>
          <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
            Attestix exposes the full compliance surface as MCP tools, REST
            endpoints and a Python library. Each module is independently
            testable, cryptographically self-contained, and conformant to the
            W3C, UCAN and RFC standards it implements.
          </p>
        </div>

        <div className="mt-14 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {ATX_MODULES.map((m) => (
            <article
              key={m.n}
              className="group flex flex-col rounded-atx-md border border-atx-line-soft bg-atx-panel p-6 transition-colors hover:border-atx-accent/60 hover:bg-atx-panel-hi"
            >
              <div className="flex items-center justify-between font-mono-atx text-[11px] uppercase tracking-[0.12em] text-atx-ink-faint">
                <span>{m.n} / 09</span>
                <span className="text-atx-ink-dim">{m.tools} tools</span>
              </div>

              <div className="mt-5 text-[28px] text-atx-accent">
                <AtxIcon name={m.icon} />
              </div>

              <h3 className="mt-3 font-serif text-[22px] leading-tight text-atx-ink">
                {m.name}
              </h3>
              <p className="mt-2 text-[13.5px] leading-[1.55] text-atx-ink-mid">
                {m.desc}
              </p>

              <div className="mt-5 flex flex-wrap gap-1.5">
                {m.pills.map((p) => (
                  <span
                    key={p}
                    className="rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-2 py-0.5 font-mono-atx text-[10.5px] text-atx-ink-dim"
                  >
                    {p}
                  </span>
                ))}
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
