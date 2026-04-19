"use client";

import { useState } from "react";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";

type Status = "shipped" | "partial" | "roadmap";
type Audience = "all" | "provider" | "deployer" | "high";

interface Row {
  article: string;
  title: string;
  evidence: string;
  tool: string;
  status: Status;
  audience: Audience[];
}

const ROWS: Row[] = [
  {
    article: "Article 5",
    title: "Prohibited practices enforcement",
    evidence: "Block self-assessment for prohibited-adjacent agents.",
    tool: "compliance.create_compliance_profile",
    status: "shipped",
    audience: ["all"],
  },
  {
    article: "Article 9",
    title: "Risk management system",
    evidence: "Risk-tier profile with unfolded obligations.",
    tool: "compliance.create_compliance_profile",
    status: "shipped",
    audience: ["provider", "high"],
  },
  {
    article: "Article 10",
    title: "Data governance",
    evidence: "Training data provenance, bias test attachments.",
    tool: "provenance.record_training_data",
    status: "shipped",
    audience: ["provider", "high"],
  },
  {
    article: "Article 11",
    title: "Technical documentation",
    evidence: "Model lineage records with eval metrics.",
    tool: "provenance.record_model_lineage",
    status: "shipped",
    audience: ["provider", "high"],
  },
  {
    article: "Article 12",
    title: "Record keeping",
    evidence: "Hash-chained audit trail, tamper-evident.",
    tool: "provenance.log_action",
    status: "shipped",
    audience: ["provider", "deployer", "high"],
  },
  {
    article: "Article 13",
    title: "Transparency",
    evidence: "Agent card at /.well-known/agent.json.",
    tool: "identity.generate_agent_card",
    status: "shipped",
    audience: ["provider", "deployer"],
  },
  {
    article: "Article 14",
    title: "Human oversight",
    evidence: "Delegation with attenuation, revocation.",
    tool: "delegation.create_delegation",
    status: "shipped",
    audience: ["provider", "deployer", "high"],
  },
  {
    article: "Article 15",
    title: "Accuracy and robustness",
    evidence: "Reputation scoring, performance baselines.",
    tool: "reputation.record_interaction",
    status: "shipped",
    audience: ["provider", "high"],
  },
  {
    article: "Article 43",
    title: "Conformity assessment",
    evidence: "Third-party enforcement, notified body capture.",
    tool: "compliance.record_conformity_assessment",
    status: "shipped",
    audience: ["provider", "high"],
  },
  {
    article: "Annex V",
    title: "Declaration of Conformity",
    evidence: "Auto-issued W3C VC with Ed25519 proof.",
    tool: "compliance.generate_declaration_of_conformity",
    status: "shipped",
    audience: ["provider", "high"],
  },
  {
    article: "Article 72",
    title: "Post-market monitoring",
    evidence: "Ongoing reputation + audit trail feed.",
    tool: "reputation.query_reputation",
    status: "partial",
    audience: ["provider"],
  },
  {
    article: "Article 73",
    title: "Serious incident reporting",
    evidence: "Incident credential issuance pattern.",
    tool: "credentials.issue_credential",
    status: "partial",
    audience: ["provider", "deployer"],
  },
  {
    article: "Annex III",
    title: "High-risk use-case list",
    evidence: "Automatic classification from intended purpose.",
    tool: "compliance.create_compliance_profile",
    status: "shipped",
    audience: ["provider"],
  },
];

const STATUS_STYLE: Record<Status, string> = {
  shipped: "border-atx-ok/40 bg-atx-ok/[0.08] text-atx-ok",
  partial: "border-atx-warn/40 bg-atx-warn/[0.08] text-atx-warn",
  roadmap: "border-atx-info/40 bg-atx-info/[0.08] text-atx-info",
};
const STATUS_LABEL: Record<Status, string> = {
  shipped: "shipped",
  partial: "partial",
  roadmap: "roadmap",
};

const FILTERS: { slug: Audience; label: string }[] = [
  { slug: "all", label: "All" },
  { slug: "high", label: "High-risk only" },
  { slug: "provider", label: "Provider" },
  { slug: "deployer", label: "Deployer" },
];

export function ComplianceMatrixSection() {
  const [filter, setFilter] = useState<Audience>("all");
  const rows = ROWS.filter(
    (r) => filter === "all" || r.audience.includes(filter)
  );

  return (
    <section id="compliance-matrix" className="border-t border-atx-line-soft py-24">
      <div className="mx-auto max-w-[1320px] px-7">
        <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
          <div>
            <AtxEyebrow number="09">Compliance matrix</AtxEyebrow>
            <h2 className="mt-3 font-serif text-[clamp(28px,3.2vw,40px)] leading-[1.15] tracking-[-0.01em] text-atx-ink">
              Every article,
              <br />
              mapped to a
              <br />
              <em className="italic text-atx-accent">tool call.</em>
            </h2>
          </div>
          <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
            Thirteen EU AI Act articles and annexes. Each row names the
            evidence Attestix produces and the exact MCP tool that emits it.
            Filter by audience (provider, deployer) or risk tier (high-risk
            only) to see the obligations that apply to your role.
          </p>
        </div>

        <div className="mt-10 flex flex-wrap gap-2">
          {FILTERS.map((f) => {
            const active = filter === f.slug;
            return (
              <button
                key={f.slug}
                type="button"
                onClick={() => setFilter(f.slug)}
                className={`inline-flex h-8 items-center rounded-atx-sm border px-3 font-mono-atx text-[11px] uppercase tracking-[0.14em] transition-colors ${
                  active
                    ? "border-atx-accent/60 bg-atx-accent-soft text-atx-accent"
                    : "border-atx-line bg-atx-panel text-atx-ink-dim hover:border-atx-ink-dim hover:text-atx-ink"
                }`}
              >
                {f.label}
              </button>
            );
          })}
        </div>

        <div className="mt-6 overflow-hidden rounded-atx-md border border-atx-line-soft">
          <table className="w-full border-collapse text-left text-[13px]">
            <thead className="bg-atx-bg-sunken">
              <tr>
                <th className="border-b border-atx-line-soft px-5 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                  Article
                </th>
                <th className="border-b border-atx-line-soft px-5 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                  Obligation
                </th>
                <th className="hidden border-b border-atx-line-soft px-5 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint md:table-cell">
                  Attestix tool
                </th>
                <th className="border-b border-atx-line-soft px-5 py-3 text-right font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                  Status
                </th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr
                  key={`${r.article}-${i}`}
                  className="bg-atx-panel transition-colors hover:bg-atx-panel-hi"
                >
                  <td className="border-b border-atx-line-soft px-5 py-4 font-mono-atx text-[12px] text-atx-accent">
                    {r.article}
                  </td>
                  <td className="border-b border-atx-line-soft px-5 py-4">
                    <div className="text-atx-ink">{r.title}</div>
                    <div className="mt-1 text-[12.5px] text-atx-ink-mid">
                      {r.evidence}
                    </div>
                  </td>
                  <td className="hidden border-b border-atx-line-soft px-5 py-4 font-mono-atx text-[11.5px] text-atx-ink-dim md:table-cell">
                    {r.tool}
                  </td>
                  <td className="border-b border-atx-line-soft px-5 py-4 text-right">
                    <span
                      className={`inline-block rounded-atx-xs border px-2 py-0.5 font-mono-atx text-[10.5px] uppercase tracking-[0.12em] ${STATUS_STYLE[r.status]}`}
                    >
                      {STATUS_LABEL[r.status]}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
