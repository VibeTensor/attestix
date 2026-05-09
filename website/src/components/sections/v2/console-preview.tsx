import Link from "next/link";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";

function PreviewCard() {
  return (
    <div className="overflow-hidden rounded-atx-md border border-atx-line-soft bg-atx-panel shadow-[var(--atx-shadow-md)]">
      <div className="flex items-center gap-3 border-b border-atx-line-soft px-4 py-2.5 font-mono-atx text-[11px] text-atx-ink-dim">
        <span className="flex gap-1.5">
          <span className="inline-block h-2 w-2 rounded-full bg-atx-err/60" />
          <span className="inline-block h-2 w-2 rounded-full bg-atx-warn/60" />
          <span className="inline-block h-2 w-2 rounded-full bg-atx-ok/60" />
        </span>
        <span>Attestix Console / localhost:8501</span>
        <span className="ml-auto flex items-center gap-2 text-atx-ok">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-atx-ok" />
          connected
        </span>
      </div>

      <div className="grid grid-cols-[180px_1fr]">
        <nav className="border-r border-atx-line-soft bg-atx-bg-sunken p-3">
          <div className="mb-2 font-mono-atx text-[9.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
            Operate
          </div>
          {[
            { l: "Agents", n: 8, active: true },
            { l: "Compliance", n: 6 },
            { l: "Credentials", n: 2 },
            { l: "Audit trail", n: 10 },
            { l: "Anchors", n: 7 },
          ].map((s) => (
            <div
              key={s.l}
              className={`flex items-center justify-between rounded-atx-xs px-2 py-1.5 font-mono-atx text-[11px] ${
                s.active
                  ? "bg-atx-panel-hi text-atx-accent"
                  : "text-atx-ink-dim"
              }`}
            >
              <span>{s.l}</span>
              <span className="text-[10px] text-atx-ink-faint">{s.n}</span>
            </div>
          ))}
        </nav>

        <div className="p-5">
          <div className="flex items-center justify-between">
            <div className="font-serif text-[22px] leading-none text-atx-ink">
              Agents
            </div>
            <div className="font-mono-atx text-[11px] text-atx-ink-dim">
              8 / 8 agents
            </div>
          </div>

          <table className="mt-4 w-full text-left font-mono-atx text-[11px]">
            <thead>
              <tr className="text-atx-ink-faint">
                <th className="pb-2 font-medium">Agent</th>
                <th className="pb-2 font-medium">Risk</th>
                <th className="pb-2 font-medium">Status</th>
                <th className="pb-2 text-right font-medium">Trust</th>
              </tr>
            </thead>
            <tbody>
              {[
                { n: "quarterly-analyst-v2", r: "HIGH", s: "compl", t: 94 },
                { n: "clinical-triage-bot", r: "HIGH", s: "gap", t: 78 },
                { n: "supply-chain-optimizer", r: "LIM", s: "compl", t: 89 },
                { n: "fraud-detector", r: "PRO", s: "compl", t: 96 },
                { n: "doc-summarizer", r: "MIN", s: "compl", t: 91 },
              ].map((a) => (
                <tr
                  key={a.n}
                  className="border-t border-atx-line-soft/60 text-atx-ink"
                >
                  <td className="py-2">{a.n}</td>
                  <td className="py-2 text-atx-accent">{a.r}</td>
                  <td className="py-2">
                    <span
                      aria-label={
                        a.s === "compl"
                          ? "compliant"
                          : a.s === "gap"
                            ? "gaps"
                            : "revoked"
                      }
                      role="img"
                      className={`inline-block h-1.5 w-1.5 rounded-full ${
                        a.s === "compl"
                          ? "bg-atx-ok"
                          : a.s === "gap"
                            ? "bg-atx-warn"
                            : "bg-atx-err"
                      }`}
                    />
                  </td>
                  <td className="py-2 text-right">
                    <div className="inline-flex items-center gap-2">
                      <span className="block h-0.5 w-10 rounded-full bg-atx-line-soft">
                        <span
                          className="block h-0.5 rounded-full bg-atx-accent"
                          style={{ width: `${a.t}%` }}
                        />
                      </span>
                      <span className="text-atx-ink-dim">
                        {(a.t / 100).toFixed(2)}
                      </span>
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
    <section
      id="console-preview"
      className="border-t border-atx-line-soft py-24"
    >
      <div className="mx-auto max-w-[1320px] px-7">
        <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
          <div>
            <AtxEyebrow number="04">The product</AtxEyebrow>
            <h2 className="mt-3 font-serif text-[clamp(28px,3.2vw,40px)] leading-[1.15] tracking-[-0.01em] text-atx-ink">
              A console that
              <br />
              behaves like
              <br />
              <em className="italic text-atx-accent">compliance.</em>
            </h2>
          </div>
          <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
            Every agent, every credential, every hash. The Attestix console is
            a working surface across the full stack with the same primitives
            the CLI, MCP server, and REST API expose.
          </p>
        </div>

        <div className="mt-14 flex flex-col gap-5">
          <PreviewCard />
          <div className="flex flex-wrap items-center gap-3">
            <Link
              href="/console"
              className="group inline-flex h-10 items-center gap-2 rounded-atx-md bg-atx-accent px-5 text-[13px] font-medium text-[oklch(0.14_0.01_180)] transition-colors hover:bg-atx-accent-deep"
            >
              Launch interactive console
              <span className="font-mono-atx transition-transform group-hover:translate-x-0.5">
                &rarr;
              </span>
            </Link>
            <span className="font-mono-atx text-[11px] uppercase tracking-[0.1em] text-atx-ink-faint">
              data is simulated
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
