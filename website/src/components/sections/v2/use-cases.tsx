import { AtxEyebrow } from "@/components/atx/atx-eyebrow";

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

const TIER_STYLE: Record<RiskTier, string> = {
  prohibited: "border-atx-err/40 bg-atx-err/[0.08] text-atx-err",
  high: "border-atx-accent/40 bg-atx-accent-soft text-atx-accent",
  limited: "border-atx-info/40 bg-atx-info/[0.08] text-atx-info",
  minimal: "border-atx-ok/40 bg-atx-ok/[0.08] text-atx-ok",
};

const USE_CASES: UseCase[] = [
  {
    id: "financial",
    agentName: "quarterly-analyst-v2",
    industry: "Financial services",
    tier: "high",
    article: "Article 43",
    summary:
      "Analyses quarterly financial data, generates regulatory reports, and produces narrative summaries for board review. Sits in the Annex III high-risk list under credit scoring and financial automation.",
    outcome:
      "Third-party conformity assessment recorded, Annex V declaration auto-issued as a W3C VC, every analysis call hash-chained into the audit trail.",
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
    tier: "prohibited",
    article: "Article 5",
    summary:
      "CV pre-screening agent for shortlisting candidates. Sits adjacent to prohibited practices if used for automated decisions without human oversight.",
    outcome:
      "Attestix blocks self-assessment, forces third-party conformity, and halts credential issuance if bias audit fails. Revocation is tamper-evident on the hash chain.",
  },
  {
    id: "logistics",
    agentName: "supply-chain-optimizer",
    industry: "Logistics",
    tier: "limited",
    article: "Article 52",
    summary:
      "Optimises supplier routing and inventory levels across warehouses. Limited-risk under the EU AI Act. Transparency obligations apply.",
    outcome:
      "Agent identity card published at /.well-known/agent.json, delegations to sub-agents tracked as UCAN, reputation score updated per interaction.",
  },
];

export function UseCasesSection() {
  return (
    <section id="use-cases" className="border-t border-atx-line-soft py-24">
      <div className="mx-auto max-w-[1320px] px-7">
        <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
          <div>
            <AtxEyebrow number="07">Use cases</AtxEyebrow>
            <h2 className="mt-3 font-serif text-[clamp(28px,3.2vw,40px)] leading-[1.15] tracking-[-0.01em] text-atx-ink">
              Four agents,
              <br />
              four risk tiers,
              <br />
              <em className="italic text-atx-accent">one toolkit.</em>
            </h2>
          </div>
          <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
            Every EU AI Act risk tier maps to the same Attestix workflow, with
            different obligations automatically unfolded. Examples below are
            illustrative. Real deployments configure their own agent names,
            issuers, and notified bodies.
          </p>
        </div>

        <div className="mt-14 grid gap-5 md:grid-cols-2">
          {USE_CASES.map((u) => (
            <article
              key={u.id}
              className="flex flex-col gap-4 rounded-atx-md border border-atx-line-soft bg-atx-panel p-7"
            >
              <div className="flex flex-wrap items-center gap-3">
                <span
                  className={`rounded-atx-xs border px-2 py-0.5 font-mono-atx text-[10.5px] uppercase tracking-[0.12em] ${TIER_STYLE[u.tier]}`}
                >
                  {TIER_LABEL[u.tier]}
                </span>
                <span className="font-mono-atx text-[10.5px] uppercase tracking-[0.12em] text-atx-ink-faint">
                  {u.article}
                </span>
                <span className="ml-auto font-mono-atx text-[10.5px] uppercase tracking-[0.12em] text-atx-ink-dim">
                  {u.industry}
                </span>
              </div>

              <h3 className="font-mono-atx text-[15px] text-atx-ink">
                <span className="text-atx-accent">attestix:</span>
                {u.agentName}
              </h3>

              <p className="text-[13.5px] leading-[1.6] text-atx-ink-mid">
                {u.summary}
              </p>

              <div className="mt-auto rounded-atx-sm border border-atx-line-soft bg-atx-bg-sunken p-4">
                <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                  Attestix output
                </div>
                <p className="mt-2 text-[13px] leading-[1.55] text-atx-ink">
                  {u.outcome}
                </p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
