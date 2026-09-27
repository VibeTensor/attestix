import Link from "next/link";
import { ArrowRight } from "lucide-react";

const WRAP = "mx-auto w-full max-w-[1200px] px-6";
const H2 = "text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink";
const LEAD = "text-[17.5px] leading-[1.6] text-atx-ink-mid";

// Also rendered by home/home-demo.tsx.
export function PreviewCard() {
  return (
    <div className="overflow-hidden rounded-2xl border border-atx-line bg-atx-panel shadow-[var(--atx-shadow-md)]">
      <div className="flex items-center gap-3 border-b border-atx-line-soft px-4 py-2.5 text-[12px] text-atx-ink-dim">
        <span className="flex gap-1.5">
          <span className="inline-block h-2 w-2 rounded-full bg-atx-err/60" />
          <span className="inline-block h-2 w-2 rounded-full bg-atx-warn/60" />
          <span className="inline-block h-2 w-2 rounded-full bg-atx-ok/60" />
        </span>
        <span>
          Attestix Console / <span className="font-mono-atx">attestix.io/console</span>
        </span>
        <span className="ml-auto flex items-center gap-2 text-atx-ok">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-atx-ok" />
          connected
        </span>
      </div>

      <div className="grid grid-cols-[150px_1fr] sm:grid-cols-[180px_1fr]">
        <nav className="border-r border-atx-line-soft bg-atx-bg-sunken p-3">
          <div className="mb-2 px-2 text-[12px] font-medium text-atx-ink-dim">Operate</div>
          {[
            { l: "Agents", n: 8, active: true },
            { l: "Compliance", n: 6 },
            { l: "Credentials", n: 2 },
            { l: "Audit trail", n: 10 },
            { l: "Anchors", n: 7 },
          ].map((s) => (
            <div
              key={s.l}
              className={`flex items-center justify-between rounded-md px-2 py-1.5 text-[12.5px] ${
                s.active ? "bg-atx-panel-hi text-atx-accent" : "text-atx-ink-dim"
              }`}
            >
              <span>{s.l}</span>
              <span className="text-[11px] text-atx-ink-faint">{s.n}</span>
            </div>
          ))}
        </nav>

        <div className="min-w-0 overflow-x-auto p-5">
          <div className="flex items-center justify-between">
            <div className="text-[19px] font-semibold leading-none tracking-[-0.48px] text-atx-ink">
              Agents
            </div>
            <div className="text-[12px] text-atx-ink-dim">8 / 8 agents</div>
          </div>

          <table className="mt-4 w-full text-left text-[11.5px]">
            <thead>
              <tr className="text-[12px] text-atx-ink-dim">
                <th className="pb-2 font-medium">Agent</th>
                <th className="pb-2 font-medium">Risk</th>
                <th className="pb-2 font-medium">Status</th>
                <th className="pb-2 text-right font-medium">Trust</th>
              </tr>
            </thead>
            <tbody className="font-mono-atx">
              {[
                { n: "quarterly-analyst-v2", r: "HIGH", s: "compl", t: 94 },
                { n: "clinical-triage-bot", r: "HIGH", s: "gap", t: 78 },
                { n: "supply-chain-optimizer", r: "LIM", s: "compl", t: 89 },
                { n: "fraud-detector", r: "MIN", s: "compl", t: 96 },
                { n: "doc-summarizer", r: "MIN", s: "compl", t: 91 },
              ].map((a) => (
                <tr key={a.n} className="border-t border-atx-line-soft/60 text-atx-ink">
                  <td className="py-2 pr-3">{a.n}</td>
                  <td className="py-2 pr-3 text-atx-accent">{a.r}</td>
                  <td className="py-2 pr-3">
                    <span
                      aria-label={a.s === "compl" ? "compliant" : a.s === "gap" ? "gaps" : "revoked"}
                      role="img"
                      className={`inline-block h-1.5 w-1.5 rounded-full ${
                        a.s === "compl" ? "bg-atx-ok" : a.s === "gap" ? "bg-atx-warn" : "bg-atx-err"
                      }`}
                    />
                  </td>
                  <td className="py-2 text-right">
                    <div className="inline-flex items-center gap-2">
                      <span className="block h-0.5 w-10 rounded-full bg-atx-line-soft">
                        <span className="block h-0.5 rounded-full bg-atx-accent" style={{ width: `${a.t}%` }} />
                      </span>
                      <span className="text-atx-ink-dim">{(a.t / 100).toFixed(2)}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export function ConsolePreviewSection() {
  return (
    <section id="console-preview" className="scroll-mt-20 bg-atx-bg-elev py-20">
      <div className={WRAP}>
        <div className="text-center">
          <h2 className={H2}>
            A console that behaves like <span className="text-atx-accent">compliance</span>
          </h2>
          <p className={`mx-auto mt-4 max-w-[760px] ${LEAD}`}>
            Every agent, every credential, every hash. The Attestix console is
            a working surface across the full stack with the same primitives
            the CLI, MCP server, and REST API expose.
          </p>
        </div>

        <div className="mx-auto mt-12 max-w-[1040px]">
          <PreviewCard />
        </div>
        <div className="mt-8 flex flex-col items-center gap-3">
          <Link
            href="/console"
            className="group inline-flex items-center gap-2 rounded-full bg-atx-accent px-6 py-3 text-[15px] font-medium text-[oklch(0.14_0.01_180)] transition-colors duration-200 hover:bg-atx-accent-deep"
          >
            Launch interactive console
            <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5" />
          </Link>
          <span className="text-[13px] text-atx-ink-dim">Data is simulated.</span>
        </div>
      </div>
    </section>
  );
}
