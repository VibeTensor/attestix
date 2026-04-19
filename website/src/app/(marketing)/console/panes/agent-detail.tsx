"use client";

import { useState } from "react";
import {
  CONSOLE_CREDENTIALS,
  RISK_LABEL,
  STATUS_LABEL,
  type ConsoleAgent,
  type ConsoleAudit,
} from "@/lib/atx-console-data";
import { AtxCopyText } from "@/components/atx/atx-copy-text";
import { AtxIcon } from "@/components/atx/atx-icons";
import { CredentialCard } from "./vc-pane";
import { AuditList } from "./audit-pane";
import { AnchorsChain } from "./anchors-pane";

interface Props {
  agent: ConsoleAgent;
  audit: ConsoleAudit[];
  onBack: () => void;
}

const TABS = ["overview", "compliance", "credentials", "audit", "anchors"] as const;
type Tab = (typeof TABS)[number];

export function AgentDetail({ agent, audit, onBack }: Props) {
  const [tab, setTab] = useState<Tab>("overview");
  return (
    <div>
      <button
        type="button"
        onClick={onBack}
        className="inline-flex items-center gap-1.5 font-mono-atx text-[11.5px] uppercase tracking-[0.12em] text-atx-ink-dim hover:text-atx-accent"
      >
        <AtxIcon name="arrowBack" /> back to agents
      </button>

      <div className="mt-4 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="font-serif text-[32px] leading-none text-atx-ink">
            {agent.displayName}
          </h2>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <Badge tone="risk" risk={agent.risk} />
            <Badge tone="status" status={agent.status} />
            {agent.anchored && (
              <span className="inline-block rounded-atx-xs border border-atx-accent/40 bg-atx-accent-soft px-2 py-0.5 font-mono-atx text-[10px] uppercase tracking-[0.12em] text-atx-accent">
                &#9673; anchored
              </span>
            )}
          </div>
          <div className="mt-3 break-all font-mono-atx text-[12px] text-atx-ink-dim">
            {agent.did}
          </div>
          <div className="mt-1 font-mono-atx text-[11.5px] text-atx-ink-faint">
            {agent.id}
          </div>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            className="inline-flex h-8 items-center gap-1.5 rounded-atx-sm border border-atx-line px-3 font-mono-atx text-[11px] text-atx-ink hover:border-atx-ink-dim"
          >
            <AtxIcon name="cred" /> issue VC
          </button>
          <button
            type="button"
            className="inline-flex h-8 items-center gap-1.5 rounded-atx-sm border border-atx-line px-3 font-mono-atx text-[11px] text-atx-ink hover:border-atx-ink-dim"
          >
            <AtxIcon name="chain" /> anchor
          </button>
          <button
            type="button"
            className="inline-flex h-8 items-center rounded-atx-sm border border-atx-err/40 bg-atx-err/[0.08] px-3 font-mono-atx text-[11px] text-atx-err hover:bg-atx-err/[0.15]"
          >
            revoke
          </button>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <Metric k="Trust score" v={agent.trust.toFixed(2)} suffix=" / 1.00" />
        <Metric k="Interactions" v={agent.interactions.toLocaleString()} />
        <Metric
          k="Credentials / delegations"
          v={String(agent.credentials)}
          suffix={` / ${agent.delegations}`}
        />
      </div>

      <div className="mt-6 border-b border-atx-line-soft">
        <div className="flex flex-wrap gap-1">
          {TABS.map((t) => {
            const active = tab === t;
            return (
              <button
                key={t}
                type="button"
                onClick={() => setTab(t)}
                className={`relative px-4 py-2.5 font-mono-atx text-[11px] uppercase tracking-[0.14em] transition-colors ${
                  active
                    ? "text-atx-accent after:absolute after:inset-x-0 after:bottom-[-1px] after:h-[2px] after:bg-atx-accent"
                    : "text-atx-ink-dim hover:text-atx-ink"
                }`}
              >
                {t === "audit" ? "Audit trail" : t}
              </button>
            );
          })}
        </div>
      </div>

      <div className="mt-6">
        {tab === "overview" && <AgentOverview agent={agent} />}
        {tab === "compliance" && <ComplianceProfile agent={agent} />}
        {tab === "credentials" && (
          <div className="space-y-4">
            {CONSOLE_CREDENTIALS.map((c) => (
              <CredentialCard key={c.id} c={c} />
            ))}
          </div>
        )}
        {tab === "audit" && (
          <AuditList
            items={audit.filter(
              (e) => e.actor === agent.id || e.target === agent.id
            )}
          />
        )}
        {tab === "anchors" && <AnchorsChain agent={agent} />}
      </div>
    </div>
  );
}

function Metric({
  k,
  v,
  suffix,
}: {
  k: string;
  v: string;
  suffix?: string;
}) {
  return (
    <div className="rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-5">
      <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
        {k}
      </div>
      <div className="mt-2 font-serif text-[32px] leading-none text-atx-ink">
        {v}
        {suffix ? (
          <span className="font-mono-atx text-[12px] text-atx-ink-dim">
            {suffix}
          </span>
        ) : null}
      </div>
    </div>
  );
}

function Badge({
  tone,
  risk,
  status,
}: {
  tone: "risk" | "status";
  risk?: ConsoleAgent["risk"];
  status?: ConsoleAgent["status"];
}) {
  if (tone === "risk" && risk) {
    const cls: Record<typeof risk, string> = {
      prohibited: "border-atx-err/40 bg-atx-err/[0.08] text-atx-err",
      high: "border-atx-accent/40 bg-atx-accent-soft text-atx-accent",
      limited: "border-atx-info/40 bg-atx-info/[0.08] text-atx-info",
      minimal: "border-atx-ok/40 bg-atx-ok/[0.08] text-atx-ok",
    };
    return (
      <span
        className={`inline-block rounded-atx-xs border px-2 py-0.5 font-mono-atx text-[10px] uppercase tracking-[0.12em] ${cls[risk]}`}
      >
        {RISK_LABEL[risk]}
      </span>
    );
  }
  if (tone === "status" && status) {
    const cls: Record<typeof status, string> = {
      compl: "border-atx-ok/40 bg-atx-ok/[0.08] text-atx-ok",
      gap: "border-atx-warn/40 bg-atx-warn/[0.08] text-atx-warn",
      rev: "border-atx-err/40 bg-atx-err/[0.08] text-atx-err",
      pend: "border-atx-info/40 bg-atx-info/[0.08] text-atx-info",
    };
    return (
      <span
        className={`inline-block rounded-atx-xs border px-2 py-0.5 font-mono-atx text-[10px] uppercase tracking-[0.12em] ${cls[status]}`}
      >
        {STATUS_LABEL[status]}
      </span>
    );
  }
  return null;
}

function AgentOverview({ agent }: { agent: ConsoleAgent }) {
  return (
    <div>
      <blockquote className="mb-6 border-l-2 border-atx-accent pl-4 font-serif text-[18px] leading-[1.4] text-atx-ink">
        &ldquo;{agent.description}&rdquo;
      </blockquote>
      <div className="overflow-hidden rounded-atx-md border border-atx-line-soft">
        <DataRow
          k="Agent ID"
          v={<AtxCopyText value={agent.id}>{agent.id}</AtxCopyText>}
          mono
        />
        <DataRow
          k="DID"
          v={<AtxCopyText value={agent.did}>{agent.did}</AtxCopyText>}
          mono
        />
        <DataRow k="Verification method" v="Ed25519VerificationKey2020" mono />
        <DataRow k="Issuer" v={agent.issuer} />
        <DataRow
          k="Protocol binding"
          v={`${agent.protocol.toUpperCase()} / MCP / A2A`}
          mono
        />
        <DataRow k="Capabilities" v={agent.capabilities.join(", ")} mono />
        <DataRow
          k="Created / expires"
          v={`${agent.created} / ${agent.expiry}`}
          mono
        />
        {agent.anchorTxn ? (
          <DataRow
            k="Base L2 anchor"
            v={
              <AtxCopyText value={agent.anchorTxn}>
                {`${agent.anchorTxn.slice(0, 22)}...${agent.anchorTxn.slice(-6)}`}
              </AtxCopyText>
            }
            mono
          />
        ) : null}
      </div>
    </div>
  );
}

function DataRow({
  k,
  v,
  mono,
}: {
  k: string;
  v: React.ReactNode;
  mono?: boolean;
}) {
  return (
    <div className="grid grid-cols-[160px_1fr] items-baseline gap-4 border-b border-atx-line-soft bg-atx-panel px-4 py-3 last:border-b-0">
      <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
        {k}
      </div>
      <div
        className={`break-all ${mono ? "font-mono-atx text-[11.5px]" : "text-[13.5px]"} text-atx-ink`}
      >
        {v}
      </div>
    </div>
  );
}

interface ComplianceItem {
  article: string;
  name: string;
  done: boolean;
}

function ComplianceProfile({ agent }: { agent: ConsoleAgent }) {
  const items: ComplianceItem[] = [
    { article: "Article 9", name: "Risk management system", done: true },
    {
      article: "Article 10",
      name: "Data and data governance",
      done: agent.status !== "rev",
    },
    { article: "Article 11", name: "Technical documentation", done: true },
    { article: "Article 12", name: "Record keeping", done: true },
    {
      article: "Article 13",
      name: "Transparency and provision of information",
      done: agent.status === "compl",
    },
    {
      article: "Article 14",
      name: "Human oversight",
      done: agent.status === "compl",
    },
    {
      article: "Article 15",
      name: "Accuracy, robustness and cybersecurity",
      done: agent.status === "compl",
    },
    {
      article: "Article 43",
      name: "Conformity assessment",
      done: agent.status === "compl",
    },
    {
      article: "Annex V",
      name: "Declaration of conformity",
      done: agent.status === "compl",
    },
  ];
  const done = items.filter((i) => i.done).length;

  return (
    <div>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
            EU AI Act / obligations checklist
          </div>
          <div className="mt-2 font-serif text-[28px] leading-none text-atx-ink">
            {done} / {items.length}{" "}
            <span className="font-mono-atx text-[12px] text-atx-ink-dim">
              complete
            </span>
          </div>
        </div>
        <button
          type="button"
          className="inline-flex h-9 items-center gap-1.5 rounded-atx-sm bg-atx-accent px-4 font-mono-atx text-[11.5px] font-medium text-[oklch(0.14_0.01_180)] hover:bg-atx-accent-deep"
        >
          Run gap analysis &rarr;
        </button>
      </div>

      <div className="mt-5 overflow-hidden rounded-atx-md border border-atx-line-soft">
        {items.map((it) => (
          <div
            key={it.article}
            className="grid grid-cols-[130px_90px_1fr_auto] items-center gap-4 border-b border-atx-line-soft bg-atx-panel px-4 py-3 last:border-b-0"
          >
            <div className="font-mono-atx text-[11px] text-atx-ink-dim">
              {it.article}
            </div>
            <div>
              <span
                className={`inline-block rounded-atx-xs border px-2 py-0.5 font-mono-atx text-[10px] uppercase tracking-[0.12em] ${
                  it.done
                    ? "border-atx-ok/40 bg-atx-ok/[0.08] text-atx-ok"
                    : "border-atx-warn/40 bg-atx-warn/[0.08] text-atx-warn"
                }`}
              >
                {it.done ? "\u2713 done" : "missing"}
              </span>
            </div>
            <div className="text-[13.5px] text-atx-ink">{it.name}</div>
            <div className="font-mono-atx text-[11px] text-atx-ink-dim">
              {it.done ? "view evidence" : "resolve \u2192"}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
