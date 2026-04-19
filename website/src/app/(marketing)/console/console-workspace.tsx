"use client";

import { useEffect, useState } from "react";
import {
  CONSOLE_AGENTS,
  CONSOLE_AUDIT_SEED,
  type ConsoleAgent,
  type ConsoleAudit,
} from "@/lib/atx-console-data";
import { AtxCreateIdentityModal } from "@/components/atx/atx-create-identity-modal";
import { AtxIcon } from "@/components/atx/atx-icons";
import type { AtxIconName } from "@/lib/atx-data";
import { AgentsPane } from "./panes/agents-pane";
import { AgentDetail } from "./panes/agent-detail";
import { CompliancePane } from "./panes/compliance-pane";
import { CredentialsPane } from "./panes/vc-pane";
import { AuditPane } from "./panes/audit-pane";
import { AnchorsPane } from "./panes/anchors-pane";
import { ComingSoonPane } from "./panes/coming-soon";

type Section =
  | "agents"
  | "compliance"
  | "credentials"
  | "audit"
  | "anchors"
  | "delegations"
  | "reputation";

interface SectionDef {
  k: Section;
  name: string;
  icon: AtxIconName;
  count: number;
}

const SECTIONS: SectionDef[] = [
  { k: "agents", name: "Agents", icon: "identity", count: CONSOLE_AGENTS.length },
  { k: "compliance", name: "Compliance", icon: "check", count: 6 },
  { k: "credentials", name: "Credentials", icon: "cred", count: 2 },
  { k: "audit", name: "Audit trail", icon: "prov", count: CONSOLE_AUDIT_SEED.length },
  { k: "anchors", name: "Anchors", icon: "chain", count: 7 },
  { k: "delegations", name: "Delegations", icon: "deleg", count: 12 },
  { k: "reputation", name: "Reputation", icon: "trust", count: 8 },
];

const TOOLS: { name: string; icon: AtxIconName; count?: number }[] = [
  { name: "MCP tools", icon: "book", count: 47 },
  { name: "REST API", icon: "ext" },
  { name: "Keys", icon: "lock" },
];

function randHashTail() {
  return Array.from(
    { length: 64 },
    () => "0123456789abcdef"[Math.floor(Math.random() * 16)]
  ).join("");
}

const ACTIONS = [
  "credential.verify",
  "action.log",
  "compliance.check",
  "reputation.update",
  "anchor.submit",
  "delegation.create",
];

export function ConsoleWorkspace() {
  const [section, setSection] = useState<Section>("agents");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [audit, setAudit] = useState<ConsoleAudit[]>(CONSOLE_AUDIT_SEED);
  const [showCreate, setShowCreate] = useState(false);

  const agent: ConsoleAgent | null = selectedId
    ? CONSOLE_AGENTS.find((a) => a.id === selectedId) ?? null
    : null;

  useEffect(() => {
    const id = window.setInterval(() => {
      setAudit((prev) => {
        const last = prev[0];
        const action = ACTIONS[Math.floor(Math.random() * ACTIONS.length)];
        const hash = `sha256:${randHashTail()}`;
        const actor = agent ? agent.id : CONSOLE_AGENTS[0].id;
        const entry: ConsoleAudit = {
          ts: new Date().toISOString(),
          action,
          actor,
          target: `${action.split(".")[0]}:${randHashTail().slice(0, 10)}`,
          hash,
          prev: last.hash,
        };
        return [entry, ...prev].slice(0, 20);
      });
    }, 12000);
    return () => window.clearInterval(id);
  }, [agent]);

  return (
    <div className="overflow-hidden rounded-atx-md border border-atx-line-soft bg-atx-panel shadow-[var(--atx-shadow-md)]">
      {/* Terminal chrome */}
      <div className="flex items-center gap-3 border-b border-atx-line-soft px-4 py-2.5">
        <span className="flex gap-1.5">
          <span className="inline-block h-2 w-2 rounded-full bg-atx-err/60" />
          <span className="inline-block h-2 w-2 rounded-full bg-atx-warn/60" />
          <span className="inline-block h-2 w-2 rounded-full bg-atx-ok/60" />
        </span>
        <span className="font-mono-atx text-[11.5px] text-atx-ink-dim">
          Attestix Console / localhost:8501
        </span>
        <span className="ml-auto flex items-center gap-2 font-mono-atx text-[11px] text-atx-ink-dim">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-atx-ok" />
          connected / did:web:vibetensor.com
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[220px_1fr]">
        {/* Sidebar */}
        <aside className="border-b border-atx-line-soft bg-atx-bg-sunken p-3 lg:border-b-0 lg:border-r">
          <div className="mb-2 px-2 font-mono-atx text-[10px] uppercase tracking-[0.14em] text-atx-ink-faint">
            Operate
          </div>
          {SECTIONS.map((s) => {
            const active = section === s.k;
            return (
              <button
                key={s.k}
                type="button"
                onClick={() => {
                  setSection(s.k);
                  setSelectedId(null);
                }}
                className={`flex w-full items-center gap-2 rounded-atx-sm px-2 py-2 text-left font-mono-atx text-[12px] transition-colors ${
                  active
                    ? "bg-atx-panel-hi text-atx-accent"
                    : "text-atx-ink-dim hover:bg-atx-panel-hi hover:text-atx-ink"
                }`}
              >
                <span className="text-[14px]">
                  <AtxIcon name={s.icon} />
                </span>
                <span className="flex-1">{s.name}</span>
                <span className="text-[10.5px] text-atx-ink-faint">
                  {s.count}
                </span>
              </button>
            );
          })}

          <div className="mb-2 mt-5 px-2 font-mono-atx text-[10px] uppercase tracking-[0.14em] text-atx-ink-faint">
            Tools
          </div>
          {TOOLS.map((t) => (
            <button
              key={t.name}
              type="button"
              disabled
              title="Demo preview. Available in the installed package."
              className="flex w-full cursor-not-allowed items-center gap-2 rounded-atx-sm px-2 py-2 text-left font-mono-atx text-[12px] text-atx-ink-faint opacity-60"
            >
              <span className="text-[14px]">
                <AtxIcon name={t.icon} />
              </span>
              <span className="flex-1">{t.name}</span>
              {t.count ? (
                <span className="text-[10.5px] text-atx-ink-faint">
                  {t.count}
                </span>
              ) : null}
            </button>
          ))}
        </aside>

        {/* Main */}
        <main className="min-w-0 overflow-x-auto p-5 sm:p-6">
          {agent ? (
            <AgentDetail
              agent={agent}
              audit={audit}
              onBack={() => setSelectedId(null)}
            />
          ) : section === "agents" ? (
            <AgentsPane
              onSelect={setSelectedId}
              openCreate={() => setShowCreate(true)}
            />
          ) : section === "compliance" ? (
            <CompliancePane onSelect={setSelectedId} />
          ) : section === "credentials" ? (
            <CredentialsPane />
          ) : section === "audit" ? (
            <AuditPane audit={audit} />
          ) : section === "anchors" ? (
            <AnchorsPane />
          ) : (
            <ComingSoonPane name={SECTIONS.find((s) => s.k === section)!.name} />
          )}
        </main>
      </div>

      {showCreate && (
        <AtxCreateIdentityModal onClose={() => setShowCreate(false)} />
      )}
    </div>
  );
}
