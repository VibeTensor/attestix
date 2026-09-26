const WRAP = "mx-auto w-full max-w-[1200px] px-6";
const H2 = "text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink";
const LEAD = "text-[17.5px] leading-[1.6] text-atx-ink-mid";

type RiskTier = "prohibited" | "high" | "limited" | "minimal";

interface UseCase {
  id: string;
  agentName: string;
  industry: string;
  tier: RiskTier;
  article: string;
  summary: string;
  outcome: string;
}

const TIER_LABEL: Record<RiskTier, string> = {
  prohibited: "Prohibited-adjacent",
  high: "High-risk",
  limited: "Limited-risk",
  minimal: "Minimal-risk",
};

const TIER_STYLE: Record<RiskTier, { card: string; chip: string }> = {
  prohibited: { card: "border-atx-err/30 bg-atx-err/[0.05]", chip: "bg-atx-err/15 text-atx-err" },
  high: { card: "border-atx-accent/30 bg-atx-accent/[0.05]", chip: "bg-atx-accent/15 text-atx-accent" },
  limited: { card: "border-atx-info/30 bg-atx-info/[0.05]", chip: "bg-atx-info/15 text-atx-info" },
  minimal: { card: "border-atx-ok/30 bg-atx-ok/[0.05]", chip: "bg-atx-ok/15 text-atx-ok" },
};

const USE_CASES: UseCase[] = [
  {
    id: "financial",
    agentName: "quarterly-analyst-v2",
    industry: "Financial services",
    tier: "high",
    article: "Annex III 5(b)",
    summary:
      "Assesses creditworthiness and generates reports for board review. Credit scoring of natural persons is high-risk under Annex III point 5(b).",
    outcome:
      "Internal-control conformity assessment (Annex VI) recorded, Annex V declaration issued as a W3C VC, every analysis call hash-chained into the audit trail.",
  },
  {
    id: "healthcare",
    agentName: "clinical-triage-bot",
    industry: "Healthcare",
    tier: "high",
    article: "Article 10",
    summary:
      "First-line patient triage for non-emergency consultations. Flags high-acuity cases for human review. Article 10 mandates strict data governance and bias testing.",
    outcome:
      "Training dataset checksums captured, demographic-parity and equal-opportunity bias tests attached, full provenance chain from data to model to action.",
  },
  {
    id: "hr",
    agentName: "hr-screener-v1",
    industry: "HR / Hiring",
    tier: "high",
    article: "Annex III 4(a)",
    summary:
      "CV pre-screening agent for shortlisting candidates. Recruitment and candidate filtering are high-risk under Annex III point 4(a), with human oversight required under Article 14.",
    outcome:
      "Risk profile, bias-testing records, and human-override events captured; the credential can be revoked if an audit fails, and revocation is tamper-evident on the hash chain.",
  },
  {
    id: "logistics",
    agentName: "supply-chain-optimizer",
    industry: "Logistics",
    tier: "limited",
    article: "Article 50",
    summary:
      "Optimises supplier routing and inventory levels across warehouses. Limited-risk under the EU AI Act. Transparency obligations apply.",
    outcome:
      "Agent identity card published at /.well-known/agent.json, delegations to sub-agents tracked as UCAN, reputation score updated per interaction.",
  },
];

export function UseCasesSection() {
  return (
    <section id="use-cases" className="scroll-mt-20 bg-atx-bg py-20">
      <div className={WRAP}>
        <div className="text-center">
          <h2 className={H2}>
            Four agents, four risk tiers, <span className="text-atx-accent">one toolkit</span>
          </h2>
          <p className={`mx-auto mt-4 max-w-[760px] ${LEAD}`}>
            Every EU AI Act risk tier maps to the same Attestix workflow, with
            different obligations automatically unfolded. Examples below are
            illustrative. Real deployments configure their own agent names,
            issuers, and notified bodies.
          </p>
        </div>

        <div className="mt-12 grid gap-5 md:grid-cols-2">
          {USE_CASES.map((u) => {
            const t = TIER_STYLE[u.tier];
            return (
              <article key={u.id} className={`flex flex-col gap-4 rounded-2xl border p-6 ${t.card}`}>
                <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
                  <span className={`rounded-full px-3 py-1 text-[13px] font-medium ${t.chip}`}>
                    {TIER_LABEL[u.tier]}
                  </span>
                  <span className="text-[13px] text-atx-ink-mid">{u.article}</span>
                  <span className="ml-auto text-[13px] text-atx-ink-dim">{u.industry}</span>
                </div>

                <h3 className="break-all font-mono-atx text-[15px] text-atx-ink">
                  <span className="text-atx-accent">attestix:</span>
                  {u.agentName}
                </h3>

                <p className="text-[15px] leading-[1.6] text-atx-ink-mid">{u.summary}</p>

                <div className="mt-auto rounded-xl border border-atx-line-soft bg-atx-bg-sunken/70 p-4">
                  <div className="text-[13px] font-medium text-atx-ink-dim">Attestix output</div>
                  <p className="mt-1.5 text-[14px] leading-[1.55] text-atx-ink">{u.outcome}</p>
                </div>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
