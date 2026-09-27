import { ATX_MODULES } from "@/lib/atx-data";
import { AtxIcon } from "@/components/atx/atx-icons";

const WRAP = "mx-auto w-full max-w-[1200px] px-6";
const H2 = "text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink";
const LEAD = "text-[17.5px] leading-[1.6] text-atx-ink-mid";

export function ModulesSection() {
  return (
    <section id="modules" className="scroll-mt-20 bg-atx-bg-elev py-20">
      <div className={WRAP}>
        <div className="text-center">
          <h2 className={H2}>
            Nine modules. <span className="text-atx-accent">Forty-seven tools.</span>
          </h2>
          <p className={`mx-auto mt-4 max-w-[760px] ${LEAD}`}>
            Attestix exposes the full compliance surface as MCP tools, REST
            endpoints and a Python library. Each module is independently
            testable and self-contained, and builds on W3C DID and Verifiable
            Credential data models, IETF RFCs, and UCAN-style delegation.
          </p>
        </div>

        <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {ATX_MODULES.map((m) => (
            <article
              key={m.n}
              className="flex flex-col rounded-2xl border border-atx-line bg-atx-panel/60 p-6 transition-colors duration-200 hover:border-atx-ink-dim"
            >
              <div className="flex items-center justify-between">
                <span className="grid h-10 w-10 place-items-center rounded-xl bg-atx-accent/15 text-[20px] text-atx-accent">
                  <AtxIcon name={m.icon} />
                </span>
                <span className="text-[13px] text-atx-ink-dim">{m.tools} tools</span>
              </div>

              <h3 className="mt-4 text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
                {m.name}
              </h3>
              <p className="mt-2 text-[14px] leading-[1.55] text-atx-ink-mid">{m.desc}</p>

              <div className="mt-5 flex flex-wrap gap-1.5">
                {m.pills.map((p) => (
                  <span
                    key={p}
                    className="rounded-md border border-atx-line-soft bg-atx-bg-sunken px-2 py-0.5 font-mono-atx text-[11px] text-atx-ink-dim"
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
