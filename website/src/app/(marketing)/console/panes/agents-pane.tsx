"use client";

import { useMemo, useState } from "react";
import {
  CONSOLE_AGENTS,
  RISK_LABEL,
  STATUS_LABEL,
  type Risk,
} from "@/lib/atx-console-data";
import { AtxIcon } from "@/components/atx/atx-icons";

const RISK_CHIPS: Array<Risk | "all"> = [
  "all",
  "prohibited",
  "high",
  "limited",
  "minimal",
];

const RISK_BADGE: Record<Risk, string> = {
  prohibited: "border-atx-err/40 bg-atx-err/[0.08] text-atx-err",
  high: "border-atx-accent/40 bg-atx-accent-soft text-atx-accent",
  limited: "border-atx-info/40 bg-atx-info/[0.08] text-atx-info",
  minimal: "border-atx-ok/40 bg-atx-ok/[0.08] text-atx-ok",
};

const STATUS_DOT = {
  compl: "bg-atx-ok",
  gap: "bg-atx-warn",
  rev: "bg-atx-err",
  pend: "bg-atx-info",
} as const;

interface Props {
  onSelect: (id: string) => void;
  openCreate: () => void;
}

export function AgentsPane({ onSelect, openCreate }: Props) {
  const [search, setSearch] = useState("");
  const [risk, setRisk] = useState<Risk | "all">("all");
  const [view, setView] = useState<"table" | "card">("table");

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return CONSOLE_AGENTS.filter((a) => {
      if (risk !== "all" && a.risk !== risk) return false;
      if (!q) return true;
      return (
        a.name.toLowerCase().includes(q) ||
        a.id.toLowerCase().includes(q) ||
        a.issuer.toLowerCase().includes(q) ||
        a.did.toLowerCase().includes(q)
      );
    });
  }, [search, risk]);

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="font-serif text-[32px] leading-none text-atx-ink">
            Agents
          </h2>
          <div className="mt-1 font-mono-atx text-[11px] uppercase tracking-[0.06em] text-atx-ink-dim">
            {filtered.length} / {CONSOLE_AGENTS.length} agents / did:web:vibetensor.com
          </div>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            className="inline-flex h-8 items-center gap-1.5 rounded-atx-sm border border-atx-line px-3 font-mono-atx text-[11.5px] text-atx-ink hover:border-atx-ink-dim"
          >
            <AtxIcon name="ext" /> export
          </button>
          <button
            type="button"
            onClick={openCreate}
            className="inline-flex h-8 items-center gap-1.5 rounded-atx-sm bg-atx-accent px-3 font-mono-atx text-[11.5px] font-medium text-[oklch(0.14_0.01_180)] hover:bg-atx-accent-deep"
          >
            <AtxIcon name="plus" /> new identity
          </button>
        </div>
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <div className="flex flex-1 min-w-[260px] items-center gap-2 rounded-atx-sm border border-atx-line bg-atx-bg-sunken px-3">
          <span className="text-atx-ink-faint">
            <AtxIcon name="search" />
          </span>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="filter / name, id, did, issuer..."
            className="h-8 flex-1 bg-transparent font-mono-atx text-[12px] text-atx-ink outline-none placeholder:text-atx-ink-dim"
          />
        </div>
        <div className="flex gap-1">
          {RISK_CHIPS.map((r) => {
            const active = risk === r;
            return (
              <button
                key={r}
                type="button"
                onClick={() => setRisk(r)}
                className={`h-7 rounded-atx-xs border px-2.5 font-mono-atx text-[10.5px] uppercase tracking-[0.1em] transition-colors ${
                  active
                    ? "border-atx-accent/60 bg-atx-accent-soft text-atx-accent"
                    : "border-atx-line-soft bg-atx-panel text-atx-ink-dim hover:text-atx-ink"
                }`}
              >
                {r === "all" ? "all" : r}
              </button>
            );
          })}
        </div>
        <div className="ml-auto flex overflow-hidden rounded-atx-sm border border-atx-line">
          {(["table", "card"] as const).map((v) => (
            <button
              key={v}
              type="button"
              onClick={() => setView(v)}
              className={`h-7 px-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] transition-colors ${
                view === v
                  ? "bg-atx-accent-soft text-atx-accent"
                  : "bg-atx-panel text-atx-ink-dim hover:text-atx-ink"
              }`}
            >
              {v === "table" ? "table" : "cards"}
            </button>
          ))}
        </div>
      </div>

      {view === "table" ? (
        <div className="mt-5 overflow-hidden rounded-atx-md border border-atx-line-soft">
          <table className="w-full text-left text-[13px]">
            <thead className="bg-atx-bg-sunken">
              <tr className="font-mono-atx text-[10px] uppercase tracking-[0.14em] text-atx-ink-faint">
                <th className="border-b border-atx-line-soft px-4 py-3 font-medium">
                  Agent
                </th>
                <th className="border-b border-atx-line-soft px-4 py-3 font-medium">
                  DID
                </th>
                <th className="hidden border-b border-atx-line-soft px-4 py-3 font-medium md:table-cell">
                  Capabilities
                </th>
                <th className="border-b border-atx-line-soft px-4 py-3 font-medium">
                  Risk
                </th>
                <th className="border-b border-atx-line-soft px-4 py-3 font-medium">
                  Status
                </th>
                <th className="border-b border-atx-line-soft px-4 py-3 font-medium">
                  Trust
                </th>
                <th className="hidden border-b border-atx-line-soft px-4 py-3 text-right font-medium lg:table-cell">
                  Last seen
                </th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((a) => (
                <tr
                  key={a.id}
                  onClick={() => onSelect(a.id)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      onSelect(a.id);
                    }
                  }}
                  tabIndex={0}
                  role="button"
                  aria-label={`Open ${a.name}`}
                  className="cursor-pointer transition-colors hover:bg-atx-panel-hi focus:bg-atx-panel-hi focus:outline-none focus-visible:ring-2 focus-visible:ring-atx-accent"
                >
                  <td className="border-b border-atx-line-soft px-4 py-3">
                    <div className="text-atx-ink">{a.name}</div>
                    <div className="mt-0.5 font-mono-atx text-[10.5px] text-atx-ink-faint">
                      {a.id}
                    </div>
                  </td>
                  <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11.5px] text-atx-ink-dim">
                    {a.did.length > 30
                      ? `${a.did.slice(0, 22)}...${a.did.slice(-8)}`
                      : a.did}
                  </td>
                  <td className="hidden border-b border-atx-line-soft px-4 py-3 md:table-cell">
                    <div className="flex flex-wrap gap-1">
                      {a.capabilities.slice(0, 2).map((c) => (
                        <span
                          key={c}
                          className="rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-1.5 py-0.5 font-mono-atx text-[10px] text-atx-ink-dim"
                        >
                          {c}
                        </span>
                      ))}
                      {a.capabilities.length > 2 && (
                        <span className="font-mono-atx text-[10px] text-atx-ink-faint">
                          +{a.capabilities.length - 2}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="border-b border-atx-line-soft px-4 py-3">
                    <span
                      className={`inline-block rounded-atx-xs border px-1.5 py-0.5 font-mono-atx text-[9.5px] uppercase tracking-[0.12em] ${RISK_BADGE[a.risk]}`}
                    >
                      {RISK_LABEL[a.risk]}
                    </span>
                  </td>
                  <td className="border-b border-atx-line-soft px-4 py-3">
                    <span className="inline-flex items-center gap-1.5 font-mono-atx text-[11px] text-atx-ink">
                      <span
                        className={`inline-block h-1.5 w-1.5 rounded-full ${STATUS_DOT[a.status]}`}
                      />
                      {STATUS_LABEL[a.status]}
                    </span>
                  </td>
                  <td className="border-b border-atx-line-soft px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className="block h-1 w-16 overflow-hidden rounded-full bg-atx-line-soft">
                        <span
                          className="block h-1 rounded-full bg-atx-accent"
                          style={{ width: `${a.trust * 100}%` }}
                        />
                      </span>
                      <span className="font-mono-atx text-[11px] text-atx-ink-dim">
                        {a.trust.toFixed(2)}
                      </span>
                    </div>
                  </td>
                  <td className="hidden border-b border-atx-line-soft px-4 py-3 text-right font-mono-atx text-[11px] text-atx-ink-faint lg:table-cell">
                    {a.created.slice(0, 10)}
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-4 py-10 text-center font-mono-atx text-[12px] text-atx-ink-dim"
                  >
                    no agents match your filter
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filtered.length === 0 && (
            <div className="col-span-full rounded-atx-md border border-atx-line-soft bg-atx-panel px-4 py-10 text-center font-mono-atx text-[12px] text-atx-ink-dim">
              no agents match your filter
            </div>
          )}
          {filtered.map((a) => (
            <button
              key={a.id}
              type="button"
              onClick={() => onSelect(a.id)}
              className="flex flex-col gap-3 rounded-atx-md border border-atx-line-soft bg-atx-panel p-5 text-left transition-colors hover:border-atx-accent/60 hover:bg-atx-panel-hi"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="font-mono-atx text-[13px] text-atx-ink">
                    {a.name}
                  </div>
                  <div className="mt-0.5 font-mono-atx text-[10.5px] text-atx-ink-faint">
                    {a.did.slice(0, 22)}...
                  </div>
                </div>
                <span
                  className={`inline-block rounded-atx-xs border px-1.5 py-0.5 font-mono-atx text-[9.5px] uppercase tracking-[0.12em] ${RISK_BADGE[a.risk]}`}
                >
                  {RISK_LABEL[a.risk]}
                </span>
              </div>
              <div className="flex flex-wrap gap-1">
                {a.capabilities.map((c) => (
                  <span
                    key={c}
                    className="rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-1.5 py-0.5 font-mono-atx text-[10px] text-atx-ink-dim"
                  >
                    {c}
                  </span>
                ))}
              </div>
              <div className="mt-auto flex items-center justify-between font-mono-atx text-[10.5px] text-atx-ink-dim">
                <span className="inline-flex items-center gap-1.5">
                  <span
                    className={`inline-block h-1.5 w-1.5 rounded-full ${STATUS_DOT[a.status]}`}
                  />
                  {STATUS_LABEL[a.status]}
                </span>
                <span>trust {a.trust.toFixed(2)}</span>
                <span>{a.interactions.toLocaleString()} int.</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
