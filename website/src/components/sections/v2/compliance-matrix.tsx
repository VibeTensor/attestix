"use client";

import { useState } from "react";

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
    evidence: "Refuses to create a profile for an unacceptable-risk (prohibited) system.",
    tool: "compliance.create_compliance_profile",
    status: "shipped",
    audience: ["all"],
  },
  {
    article: "Article 9",
    title: "Risk management system",
    evidence: "Risk-tier profile listing required obligations; the risk-management system itself is not yet tracked.",
    tool: "compliance.create_compliance_profile",
    status: "partial",
    audience: ["provider", "high"],
  },
  {
    article: "Article 10",
    title: "Data governance",
    evidence: "Signed training data records: source, licence, personal-data flag, governance measures.",
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
    evidence: "Agent card at /.well-known/agent.json; not a full set of instructions for use.",
    tool: "agent_card.generate_agent_card",
    status: "partial",
    audience: ["provider", "deployer"],
  },
  {
    article: "Article 14",
    title: "Human oversight",
    evidence: "Oversight measures on the profile; scoped, revocable delegation tokens.",
    tool: "delegation.create_delegation",
    status: "partial",
    audience: ["provider", "deployer", "high"],
  },
  {
    article: "Article 15",
    title: "Accuracy and robustness",
    evidence: "Eval metrics in model lineage; interaction-outcome reputation scoring.",
    tool: "reputation.record_interaction",
    status: "partial",
    audience: ["provider", "high"],
  },
  {
    article: "Article 43",
    title: "Conformity assessment",
    evidence: "Conformity route recorded; self-assessment refused where a notified body is required.",
    tool: "compliance.record_conformity_assessment",
    status: "shipped",
    audience: ["provider", "high"],
  },
  {
    article: "Annex V",
    title: "Declaration of Conformity",
    evidence: "Signed declaration plus an auto-issued credential with an Ed25519 proof.",
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
    evidence: "Annex III point (1-8) recorded on the profile; sets the Article 43 route.",
    tool: "compliance.create_compliance_profile",
    status: "shipped",
    audience: ["provider"],
  },
];

const STATUS_STYLE: Record<Status, string> = {
  shipped: "bg-atx-ok/15 text-atx-ok",
  partial: "bg-atx-warn/15 text-atx-warn",
  roadmap: "bg-atx-info/15 text-atx-info",
};
const STATUS_LABEL: Record<Status, string> = {
  shipped: "Shipped",
  partial: "Partial",
  roadmap: "Roadmap",
};

const FILTERS: { slug: Audience; label: string }[] = [
  { slug: "all", label: "All" },
  { slug: "high", label: "High-risk only" },
  { slug: "provider", label: "Provider" },
  { slug: "deployer", label: "Deployer" },
];

const WRAP = "mx-auto w-full max-w-[1200px] px-6";
const H2 = "text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink";
const LEAD = "text-[17.5px] leading-[1.6] text-atx-ink-mid";
const TH = "border-b border-atx-line-soft px-5 py-3.5 text-[13px] font-medium text-atx-ink-mid";

export function ComplianceMatrixSection() {
  const [filter, setFilter] = useState<Audience>("all");
  const rows = ROWS.filter(
    (r) =>
      filter === "all" ||
      r.audience.includes(filter) ||
      r.audience.includes("all")
  );

  return (
    <section id="compliance-matrix" className="scroll-mt-20 bg-atx-bg py-20">
      <div className={WRAP}>
        <div className="text-center">
          <h2 className={H2}>
            Every article, mapped to a <span className="text-atx-accent">tool call</span>
          </h2>
          <p className={`mx-auto mt-4 max-w-[760px] ${LEAD}`}>
            Thirteen EU AI Act articles and annexes. Each row names the
            evidence Attestix records and the exact MCP tool that emits it;
            &ldquo;Partial&rdquo; means Attestix covers part of the obligation.
            Filter by audience (provider, deployer) or risk tier (high-risk
            only) to see the obligations that apply to your role.
          </p>
        </div>

        <div className="mt-10 flex flex-wrap justify-center gap-2" role="group" aria-label="Filter obligations">
          {FILTERS.map((f) => {
            const active = filter === f.slug;
            return (
              <button
                key={f.slug}
                type="button"
                aria-pressed={active}
                onClick={() => setFilter(f.slug)}
                className={`inline-flex h-9 items-center rounded-full border px-4 text-[13px] font-medium transition-colors duration-200 ${
                  active
                    ? "border-atx-accent/60 bg-atx-accent/[0.08] text-atx-accent"
                    : "border-atx-line text-atx-ink-mid hover:border-atx-ink-dim hover:text-atx-ink"
                }`}
              >
                {f.label}
              </button>
            );
          })}
        </div>

        <div className="mt-6 overflow-x-auto rounded-2xl border border-atx-line">
          <table className="w-full min-w-[720px] border-collapse text-left text-[14px]">
            <thead className="bg-atx-bg-sunken">
              <tr>
                <th scope="col" className={TH}>Article</th>
                <th scope="col" className={TH}>Obligation</th>
                <th scope="col" className={TH}>Attestix tool</th>
                <th scope="col" className={`${TH} text-right`}>Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr
                  key={`${r.article}-${i}`}
                  className="bg-atx-panel/60 align-top transition-colors duration-200 hover:bg-atx-panel-hi"
                >
                  <td className="whitespace-nowrap border-b border-atx-line-soft px-5 py-4 font-medium text-atx-accent">
                    {r.article}
                  </td>
                  <td className="border-b border-atx-line-soft px-5 py-4">
                    <div className="text-atx-ink">{r.title}</div>
                    <div className="mt-1 text-[13.5px] leading-[1.5] text-atx-ink-mid">{r.evidence}</div>
                  </td>
                  <td className="border-b border-atx-line-soft px-5 py-4 font-mono-atx text-[12px] text-atx-ink-dim">
                    {r.tool}
                  </td>
                  <td className="border-b border-atx-line-soft px-5 py-4 text-right">
                    <span className={`inline-block rounded-full px-2.5 py-0.5 text-[12.5px] font-medium ${STATUS_STYLE[r.status]}`}>
                      {STATUS_LABEL[r.status]}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-center text-[13px] text-atx-ink-dim md:hidden">Scroll the table sideways to see every column.</p>
      </div>
    </section>
  );
}
