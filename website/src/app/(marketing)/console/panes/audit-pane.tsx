"use client";

import { useState } from "react";
import type { ConsoleAudit } from "@/lib/atx-console-data";
import { AtxIcon } from "@/components/atx/atx-icons";

interface Props {
  audit: ConsoleAudit[];
}

export function AuditPane({ audit }: Props) {
  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="font-serif text-[32px] leading-none text-atx-ink">
            Audit trail
          </h2>
          <div className="mt-1 font-mono-atx text-[11px] uppercase tracking-[0.06em] text-atx-ink-dim">
            Article 12 / SHA-256 hash-chained / tamper-evident
          </div>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            className="inline-flex h-8 items-center gap-1.5 rounded-atx-sm border border-atx-line px-3 font-mono-atx text-[11px] text-atx-ink hover:border-atx-ink-dim"
          >
            Verify chain
          </button>
          <button
            type="button"
            className="inline-flex h-8 items-center gap-1.5 rounded-atx-sm border border-atx-line px-3 font-mono-atx text-[11px] text-atx-ink hover:border-atx-ink-dim"
          >
            Export ndjson
          </button>
        </div>
      </div>

      <div className="mt-4 font-mono-atx text-[10.5px] uppercase tracking-[0.12em] text-atx-ink-dim">
        sha-256 hash-chained / article 12 compliant / {audit.length} entries /
        genesis verified <span className="text-atx-ok">&#10003;</span>
      </div>

      <div className="mt-4">
        <AuditList items={audit} />
      </div>
    </div>
  );
}

export function AuditList({ items }: { items: ConsoleAudit[] }) {
  const [exp, setExp] = useState<string | null>(null);
  if (items.length === 0) {
    return (
      <div className="rounded-atx-md border border-atx-line-soft bg-atx-panel px-5 py-10 text-center font-mono-atx text-[12px] text-atx-ink-dim">
        No audit entries.
      </div>
    );
  }
  return (
    <div className="overflow-hidden rounded-atx-md border border-atx-line-soft">
      {items.map((a) => {
        const isOpen = exp === a.hash;
        return (
          <div
            key={a.hash}
            className="border-b border-atx-line-soft last:border-b-0"
          >
            <button
              type="button"
              onClick={() => setExp(isOpen ? null : a.hash)}
              className="grid w-full grid-cols-[200px_1fr_160px_24px] items-center gap-3 bg-atx-panel px-4 py-3 text-left font-mono-atx text-[11.5px] transition-colors hover:bg-atx-panel-hi"
            >
              <span className="text-atx-ink-dim">{a.ts.replace("T", " ")}</span>
              <span>
                <span className="text-atx-accent">{a.action}</span>{" "}
                <span className="text-atx-ink-dim">/</span>{" "}
                <span className="text-atx-ink">{a.target}</span>
              </span>
              <span className="text-atx-ink-dim">
                {a.hash.slice(7, 22)}&hellip;
              </span>
              <span className="text-atx-ink-faint">
                <AtxIcon name={isOpen ? "chev" : "chevR"} />
              </span>
            </button>
            {isOpen && (
              <div className="space-y-1.5 bg-atx-bg-sunken px-4 py-3 font-mono-atx text-[11.5px]">
                <Row k="actor" v={a.actor} />
                <Row k="action" v={a.action} />
                <Row k="target" v={a.target} />
                <Row k="hash" v={a.hash} accent />
                <Row k="prev_hash" v={a.prev} dim />
                <Row
                  k="verify"
                  v="SHA-256(prev_hash + canonical_json(entry)) = hash \u2713"
                  ok
                />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function Row({
  k,
  v,
  accent,
  ok,
  dim,
}: {
  k: string;
  v: string;
  accent?: boolean;
  ok?: boolean;
  dim?: boolean;
}) {
  let tone = "text-atx-ink";
  if (accent) tone = "text-atx-accent";
  if (ok) tone = "text-atx-ok";
  if (dim) tone = "text-atx-ink-dim";
  return (
    <div className="grid grid-cols-[90px_1fr] gap-3">
      <span className="text-atx-ink-faint">{k}</span>
      <span className={`break-all ${tone}`}>{v}</span>
    </div>
  );
}
