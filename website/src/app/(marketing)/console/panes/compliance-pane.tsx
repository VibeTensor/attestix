"use client";

import {
  CONSOLE_AGENTS,
  RISK_LABEL,
  STATUS_LABEL,
} from "@/lib/atx-console-data";

interface Props {
  onSelect: (id: string) => void;
}

export function CompliancePane({ onSelect }: Props) {
  const compl = CONSOLE_AGENTS.filter((a) => a.status === "compl").length;
  const gap = CONSOLE_AGENTS.filter((a) => a.status === "gap").length;
  const rev = CONSOLE_AGENTS.filter((a) => a.status === "rev").length;
  const pend = CONSOLE_AGENTS.filter((a) => a.status === "pend").length;

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="font-serif text-[32px] leading-none text-atx-ink">
            Compliance
          </h2>
          <div className="mt-1 font-mono-atx text-[11px] uppercase tracking-[0.06em] text-atx-ink-dim">
            EU AI Act / gap analysis across all agents
          </div>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-4">
        <Stat k="Compliant" v={compl} tone="ok" />
        <Stat k="Gap" v={gap} tone="warn" />
        <Stat k="Revoked" v={rev} tone="err" />
        <Stat k="Pending" v={pend} tone="info" />
      </div>

      <div className="mt-6 overflow-hidden rounded-atx-md border border-atx-line-soft">
        {CONSOLE_AGENTS.map((a) => (
          <button
            key={a.id}
            type="button"
            onClick={() => onSelect(a.id)}
            className="grid w-full grid-cols-[1fr_140px_140px_100px] items-center gap-4 border-b border-atx-line-soft bg-atx-panel px-4 py-3 text-left transition-colors last:border-b-0 hover:bg-atx-panel-hi"
          >
            <div>
              <div className="text-[13.5px] text-atx-ink">{a.name}</div>
              <div className="mt-0.5 font-mono-atx text-[10.5px] text-atx-ink-faint">
                {a.id}
              </div>
            </div>
            <div className="font-mono-atx text-[11px] uppercase tracking-[0.12em] text-atx-accent">
              {RISK_LABEL[a.risk]}
            </div>
            <div className="font-mono-atx text-[11px] uppercase tracking-[0.12em] text-atx-ink-dim">
              {STATUS_LABEL[a.status]}
            </div>
            <div className="text-right font-mono-atx text-[11px] text-atx-accent">
              inspect &rarr;
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function Stat({
  k,
  v,
  tone,
}: {
  k: string;
  v: number;
  tone: "ok" | "warn" | "err" | "info";
}) {
  const color = {
    ok: "text-atx-ok",
    warn: "text-atx-warn",
    err: "text-atx-err",
    info: "text-atx-info",
  }[tone];
  return (
    <div className="rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-5">
      <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
        {k}
      </div>
      <div className={`mt-2 font-serif text-[32px] leading-none ${color}`}>
        {v}
      </div>
    </div>
  );
}
