import Link from "next/link";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "Attestix / United Kingdom",
  description:
    "Signed identity and governance evidence for UK teams evaluating AI agent workflows. Legal and regulatory applicability requires separate review.",
});

const WRAP = "mx-auto w-full max-w-[1200px] px-6";
const H2 = "text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink";
const CARD =
  "rounded-2xl border border-atx-line bg-atx-panel/60 p-6 transition-colors duration-200 hover:border-atx-ink-dim";
const LINK =
  "text-atx-accent underline decoration-atx-line underline-offset-4 transition-colors duration-200 hover:decoration-atx-accent";

const WHY_NOW = [
  {
    n: "01",
    title: "EU AI Act extraterritoriality",
    body: "UK teams serving EU markets should assess the applicable EU AI Act role, classification and staged timeline. Signed evidence supports that assessment; it does not determine legal conformity.",
  },
  {
    n: "02",
    title: "FCA outcome-based AI guidance",
    body: "Signed audit records can support accountability and oversight reviews. Their completeness, accuracy and suitability need assessment within the deploying firm's operating controls.",
  },
  {
    n: "03",
    title: "ICO data-protection-by-design",
    body: "Attestix records signed evidence and supports erasure of managed local records and parseable local backups. Remote replicas, shared credentials and external backups need separate handling. This tooling does not establish GDPR conformity.",
  },
];

const ICPS = [
  {
    city: "London",
    sector: "Fintech",
    pain: "Fintech teams evaluating agent workflows need evidence of actions, data use and delegated authority. Applicable reporting and oversight requirements depend on the firm and activity.",
    wedge: "Attestix provides signed identity records, delegated authority and hash-chained audit events. Review completeness, trusted keys and operating controls for the intended workflow.",
  },
  {
    city: "Cambridge",
    sector: "Biotech AI",
    pain: "Biotech teams may need model lineage, training-data provenance and version records. Regulatory applicability and evidence requirements depend on the product and intended use.",
    wedge: "Attestix records signed model-lineage and training-data evidence. Optional testnet anchoring has separate availability and trust requirements; it does not establish regulated retention.",
  },
  {
    city: "Edinburgh",
    sector: "Safety research",
    pain: "DeepMind-alumni and ARIA-funded safety teams need citable, reproducible provenance for monitor evaluations and red-team artifacts referenced in papers.",
    wedge: "Attestix is Apache-2.0 with a documented canonical profile and language-specific verifiers. Reviewers can verify supported signed records under an explicit trust policy; signatures do not establish claim truth.",
  },
];

const INSTALL_SNIPPET = `# Install and verify the current package version
pip install attestix

# Issue an agent identity
attestix identity create --name research-bot --did-method key

# Log a hash-chained audit event
attestix audit log "tool_call planFlights"

# Check recorded chain continuity and signatures
attestix audit verify-chain`;

export default function UKPage() {
  return (
    <>
      <section className="px-6 pb-16 pt-16 text-center md:pt-20">
        <div className="mx-auto max-w-[860px]">
          <AtxEyebrow>Region  /  United Kingdom</AtxEyebrow>
          <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
            Attestix <span className="text-atx-accent"> /  United Kingdom.</span>
          </h1>
          <div className="mx-auto mt-5 max-w-[680px] space-y-4 text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
            <p>
              Signed identity and governance evidence for UK teams evaluating AI agent workflows. Applicable requirements depend on the system, operator role and jurisdiction. The EU AI Act has a staged timeline; use its official timetable when assessing a deployment.
            </p>
            <p>
              Attestix provides open-source identity, audit and optional testnet anchoring. Cryptographic records support evidence collection across sectors; suitability for regulatory use requires separate review.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-atx-bg-elev py-20">
        <div className={WRAP}>
          <h2 className={`${H2} text-center`}>Why now for the UK</h2>
          <div className="mt-12 grid gap-5 md:grid-cols-3">
            {WHY_NOW.map((card) => (
              <article key={card.n} className={CARD}>
                <h3 className="text-[19px] font-semibold leading-[1.3] tracking-[-0.48px] text-atx-ink">
                  {card.title}
                </h3>
                <p className="mt-3 text-[15px] leading-[1.6] text-atx-ink-mid">{card.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-atx-bg py-20">
        <div className={WRAP}>
          <h2 className={`${H2} text-center`}>Who Attestix fits in the UK</h2>
          <div className="mt-12 grid gap-5 md:grid-cols-3">
            {ICPS.map((icp) => (
              <article key={icp.city} className={CARD}>
                <p className="text-[14px] font-medium text-atx-accent">{icp.sector}</p>
                <h3 className="mt-1 text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
                  {icp.city}
                </h3>
                <p className="mt-4 text-[15px] leading-[1.6] text-atx-ink-mid">
                  <span className="block text-[13px] font-medium text-atx-ink">Pain</span>
                  {icp.pain}
                </p>
                <p className="mt-4 text-[15px] leading-[1.6] text-atx-ink-mid">
                  <span className="block text-[13px] font-medium text-atx-ink">Wedge</span>
                  {icp.wedge}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-atx-bg-elev py-20">
        <div className="mx-auto w-full max-w-[860px] px-6 text-center">
          <h2 className={H2}>Evaluate the local workflow</h2>
          <p className="mx-auto mt-4 max-w-[640px] text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
            Clean Python venv, no other infrastructure. The chain verifies locally;
            anchoring to Base Sepolia testnet is optional and explicit.
          </p>
          <pre className="mt-9 overflow-x-auto rounded-xl border border-atx-line-soft bg-atx-bg-sunken p-6 text-left font-mono-atx text-[13px] leading-[1.7] text-atx-ink-mid">
            <code>{INSTALL_SNIPPET}</code>
          </pre>
          <p className="mx-auto mt-5 max-w-[680px] text-[13px] leading-[1.6] text-atx-ink-dim">
            Read the framework-specific paths at{" "}
            <Link href="/docs/quickstart" className={LINK}>
              /docs/quickstart
            </Link>
            {" "} -  LangChain, OpenAI Agents SDK, and CrewAI are real integrations
            (not example shims). Dify, Google ADK, Semantic Kernel, and Strands are
            example-only via the MCP server.
          </p>
        </div>
      </section>

      <section className="bg-atx-bg py-20">
        <div className="mx-auto w-full max-w-[860px] px-6">
          <h2 className={`${H2} text-center`}>FCA evidence  -  honesty beat</h2>
          <div className="mt-10 space-y-4 rounded-2xl border border-atx-accent/30 bg-atx-accent/[0.05] p-7 text-[15px] leading-[1.65] text-atx-ink-mid">
            <p>
              Source checks and signed records support evaluation of the tested workflow. They do not establish independent security assurance, complete capture or production acceptance. Review key custody, authenticated access, restore procedures and incident handling.
            </p>
            <p>
              Test the exact installed release and its trust limits before using production data. An accountable provider or assessor must determine applicable obligations and evidence sufficiency. Hosted offerings remain planned.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-atx-bg-elev py-20">
        <div className={WRAP}>
          <h2 className={`${H2} text-center`}>Talk to a human</h2>
          <div className="mx-auto mt-12 grid max-w-[1040px] gap-5 md:grid-cols-[1.4fr_1fr]">
            <div className="rounded-2xl border border-atx-line bg-atx-panel p-8">
              <h3 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
                Book a 30-min walkthrough
              </h3>
              <p className="mt-3 text-[15px] leading-[1.6] text-atx-ink-mid">
                Bring your governance lead, your engineering lead, and whoever
                needs to say yes. We will walk through the console end-to-end against
                a workflow you care about  -  no slide pitch.
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <Link
                  href="/demo-call?region=uk"
                  className="inline-flex items-center gap-2 rounded-full bg-atx-accent px-6 py-3 text-[15px] font-medium text-[oklch(0.14_0.01_180)] transition-colors duration-200 hover:bg-atx-accent-deep"
                >
                  Book a demo &rarr;
                </Link>
                <a
                  href="mailto:pkd@vibetensor.com?subject=%5BUK%5D%20Attestix%20demo&body=Company%3A%20%0ARole%3A%20%0AFrameworks%20in%20use%3A%20%0ARisk%20tier%3A%20%0ATimeline%3A%20"
                  className="inline-flex items-center rounded-full border border-atx-line px-6 py-3 text-[15px] font-medium text-atx-ink-mid transition-colors duration-200 hover:border-atx-ink-dim hover:text-atx-ink"
                >
                  Email pkd@vibetensor.com
                </a>
              </div>
            </div>
            <div className="rounded-2xl border border-atx-line bg-atx-panel/60 p-8">
              <h3 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
                Not ready for a call?
              </h3>
              <ul className="mt-3 space-y-2 text-[15px] leading-[1.6] text-atx-ink-mid">
                <li>
                  Try the{" "}
                  <Link href="/console" className={LINK}>
                    interactive console
                  </Link>
                </li>
                <li>
                  Read the{" "}
                  <Link href="/docs" className={LINK}>
                    docs
                  </Link>
                </li>
                <li>
                  Star the repo on{" "}
                  <a
                    href="https://github.com/VibeTensor/attestix"
                    target="_blank"
                    rel="noopener noreferrer"
                    className={LINK}
                  >
                    GitHub
                  </a>
                </li>
              </ul>
            </div>
          </div>

          <div className="mx-auto mt-12 max-w-[1040px] border-t border-atx-line-soft pt-6">
            <p className="text-[13px] font-medium text-atx-ink-mid">Compliance posture</p>
            <p className="mt-2 text-[13px] leading-[1.6] text-atx-ink-dim">
              Attestix is an evidence tool. Applicable duties depend on the system, operator role and jurisdiction. Testnet anchoring does not establish production availability or regulatory acceptance.
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
