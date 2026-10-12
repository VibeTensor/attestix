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
    <section className="mx-auto max-w-[1080px] px-7 py-24">
      <AtxEyebrow>Region / United Kingdom</AtxEyebrow>
      <h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
        Attestix
        <br />
        <em className="italic text-atx-accent">/ United Kingdom.</em>
      </h1>

      <div className="mt-10 max-w-[760px] space-y-5 text-[15px] leading-[1.65] text-atx-ink-mid">
        <p>
          Signed identity and governance evidence for UK teams evaluating AI
          agent workflows. Applicable requirements depend on the system,
          operator role and jurisdiction. The EU AI Act has a staged timeline;
          use the current official timetable when assessing a deployment.
        </p>
        <p>
          Attestix is the open-source identity, audit, and on-chain anchoring
          layer that gives AI agents the equivalent of a passport. The
          cryptographic primitives support evidence collection across sectors.
          Suitability for a specific regulatory use requires separate review.
        </p>
      </div>

      <h2 className="mt-20 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        Why now for the UK
      </h2>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        {WHY_NOW.map((card) => (
          <article
            key={card.n}
            className="rounded-atx-md border border-atx-line-soft bg-atx-panel p-6"
          >
            <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-accent">
              {card.n}
            </div>
            <div className="mt-3 font-serif text-[20px] leading-[1.15] tracking-[-0.005em] text-atx-ink">
              {card.title}
            </div>
            <p className="mt-3 text-[13.5px] leading-[1.6] text-atx-ink-mid">
              {card.body}
            </p>
          </article>
        ))}
      </div>

      <h2 className="mt-20 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        Who Attestix fits in the UK
      </h2>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        {ICPS.map((icp) => (
          <article
            key={icp.city}
            className="rounded-atx-md border border-atx-line-soft bg-atx-panel p-6"
          >
            <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
              {icp.sector}
            </div>
            <div className="mt-1 font-serif text-[22px] leading-[1.15] tracking-[-0.005em] text-atx-ink">
              {icp.city}
            </div>
            <p className="mt-4 text-[13px] leading-[1.6] text-atx-ink-mid">
              <span className="font-mono-atx text-[10.5px] uppercase tracking-[0.12em] text-atx-ink-faint">
                Pain
              </span>
              <br />
              {icp.pain}
            </p>
            <p>
              Attestix is the open-source identity, audit, and on-chain anchoring
              layer that gives AI agents the equivalent of a passport. The
              cryptographic primitives are sector-neutral, so the same evidence
              trail works under both regimes.
            </p>
          </article>
        ))}
      </div>

      <h2 className="mt-20 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        Evaluate the local workflow
      </h2>
      <p className="mt-3 max-w-[720px] text-[13.5px] leading-[1.6] text-atx-ink-mid">
        Clean Python venv, no other infrastructure. The chain verifies locally;
        anchoring to Base Sepolia testnet is optional and explicit.
      </p>
      <pre className="mt-6 overflow-x-auto rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-5 font-mono-atx text-[12.5px] leading-[1.6] text-atx-ink-mid">
        <code>{INSTALL_SNIPPET}</code>
      </pre>
      <p className="mt-4 text-[12.5px] leading-[1.55] text-atx-ink-dim">
        Read the framework-specific paths at{" "}
        <Link href="/docs/quickstart" className="text-atx-accent hover:underline">
          /docs/quickstart
        </Link>
        {" "} -  LangChain, OpenAI Agents SDK, and CrewAI are real integrations
        (not example shims). Dify, Google ADK, Semantic Kernel, and Strands are
        example-only via the MCP server.
      </p>

      <h2 className="mt-20 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        Evidence and operating limits
      </h2>
      <div className="mt-4 rounded-atx-md border border-atx-line-soft bg-atx-panel p-6 text-[13.5px] leading-[1.65] text-atx-ink-mid">
        <p>
          Source checks and signed records support evaluation of the tested
          workflow. They do not establish independent security assurance,
          complete capture or production acceptance. Review signing-key
          custody, authenticated access, restore procedures and incident
          handling for the actual deployment.
        </p>
        <p className="mt-4">
          Test the exact installed release and its documented trust limits
          before using production data. A provider or assessor must determine
          applicable obligations and whether the evidence is sufficient for
          the intended use. Hosted offerings remain planned.
        </p>
      </div>

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
          <p className="mt-4 text-[13.5px] leading-[1.6] text-atx-ink-mid">
            Bring your compliance lead, your AI engineering lead, and whoever
            needs to say yes. We will walk through the console end-to-end against
            a workflow you care about  -  no slide pitch.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              href="/demo-call?region=uk"
              className="inline-flex h-10 items-center gap-2 rounded-atx-md bg-atx-accent px-5 text-[13px] font-medium text-[oklch(0.14_0.01_180)] transition-colors hover:bg-atx-accent-deep"
            >
              Book a demo -&gt;
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
              Attestix is a single-maintainer beta with 15 GitHub stars and no
              independent third-party security audit as of v0.4.1. Open-source
              signing keys live as filesystem-mode-0600 JSON; there is no HSM/KMS
              backend in the OSS engine today.
            </p>
            <p>
              That is enough for staging, internal copilots, and pre-production
              governance pilots. For an FCA-regulated production-of-record
              deployment, the Cloud Enterprise tier (BYOK against AWS KMS Frankfurt,
              FIPS 140-2 L3) is the bridge. We name this gap because regulated UK
              buyers will ask, and an evidence tool that hides its own threat model
              fails the first audit it meets.
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
                Bring your compliance lead, your AI engineering lead, and whoever
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
              Attestix is an evidence tool, not a guarantor of compliance  -
              providers remain liable under EU AI Act Articles 16-22 regardless of
              which evidence tool they use. We do not provide legal advice. Base L2
              anchoring is Sepolia testnet only as of v0.4.1; mainnet schema
              registration is on the roadmap.
            </p>
          </div>
        </div>
        <p className="mt-3 text-[12.5px] leading-[1.6] text-atx-ink-mid">
          Attestix is an evidence tool, not a guarantor of compliance  -
          applicable duties depend on the system, operator role and
          jurisdiction. We do not provide legal advice. Testnet anchoring does
          not establish production availability or regulatory acceptance.
        </p>
      </div>
    </section>
  );
}
