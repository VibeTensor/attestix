import Link from "next/link";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "Attestix · United Kingdom",
  description:
    "AI-Act-grade evidence for UK builders selling into the EU + an FCA-aligned audit story for regulated AI. FCA, ICO, Bank of England framings.",
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
    body: "UK firms selling AI services into the EU are providers or deployers under Articles 25 and 28. The Act became generally applicable on 2 August 2026 — a UK-incorporated supplier with EU customers carries the obligations regardless of where the team sits.",
  },
  {
    n: "02",
    title: "FCA outcome-based AI guidance",
    body: "The Financial Conduct Authority puts the burden of evidence on the deploying firm — explainability, accountability, governance over AI models. A cryptographically-signed audit trail is the cheapest defence; Attestix is the evidence engine, not a model-risk-management replacement.",
  },
  {
    n: "03",
    title: "ICO data-protection-by-design",
    body: "Attestix's hash-chained audit and redaction-with-retained-hash erasure model line up with the ICO's “by design” and “demonstrable accountability” expectations. Honest scope: our GDPR coverage today is Article 17 only.",
  },
];

const ICPS = [
  {
    city: "London",
    sector: "Fintech",
    pain: "Open-banking copilots and agent-driven KYC report to the FCA under SUP 16.3 — proving which agent did what, on what data, with what authority is non-optional.",
    wedge: "Attestix issues an Ed25519-signed DID per agent, UCAN delegations per action, hash-chained audit per call. Auditable in retrospect; no vendor lock-in.",
  },
  {
    city: "Cambridge",
    sector: "Biotech AI",
    pain: "Agent-driven drug discovery is increasingly scoped under MHRA evidence requirements — model lineage, training-data provenance, and version control across pipeline steps.",
    wedge: "Attestix records the model lineage credential and training-data provenance as W3C VCs, anchored to Base Sepolia testnet for tamper-evident retention.",
  },
  {
    city: "Edinburgh",
    sector: "Safety research",
    pain: "DeepMind-alumni and ARIA-funded safety teams need citable, reproducible provenance for monitor evaluations and red-team artifacts referenced in papers.",
    wedge: "Attestix is Apache-2.0 with a published canonical-form spec and a JS verifier — a regulator or reviewer can verify our claims independently of our package.",
  },
];

const INSTALL_SNIPPET = `# Install the v0.4.1 stable
pip install attestix

# Issue an agent identity
attestix identity create --name research-bot --did-method key

# Log a hash-chained audit event
attestix audit log "tool_call planFlights"

# Verify the chain (any tampering breaks here)
attestix audit verify-chain`;

export default function UKPage() {
  return (
    <>
      <section className="px-6 pb-16 pt-16 text-center md:pt-20">
        <div className="mx-auto max-w-[860px]">
          <AtxEyebrow>Region · United Kingdom</AtxEyebrow>
          <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
            Attestix <span className="text-atx-accent">· United Kingdom.</span>
          </h1>
          <div className="mx-auto mt-5 max-w-[680px] space-y-4 text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
            <p>
              AI-Act-grade evidence for UK builders selling into the EU, and an
              FCA-aligned audit story for regulated AI. The UK is consciously
              <span className="text-atx-ink"> not </span>
              mirroring the EU horizontal regulation; each sector regulator (FCA,
              MHRA, Ofcom, ICO) brings AI rules into existing frameworks. UK firms
              exporting AI services to the EU are already inside its scope —
              so the UK market gets two regulatory regimes for the price of one.
            </p>
            <p>
              Attestix is the open-source identity, audit, and on-chain anchoring
              layer that gives AI agents the equivalent of a passport. The
              cryptographic primitives are sector-neutral, so the same evidence
              trail works under both regimes.
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
          <h2 className={H2}>What you can do in 90 seconds</h2>
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
            {" "}— LangChain, OpenAI Agents SDK, and CrewAI are real integrations
            (not example shims). Dify, Google ADK, Semantic Kernel, and Strands are
            example-only via the MCP server.
          </p>
        </div>
      </section>

      <section className="bg-atx-bg py-20">
        <div className="mx-auto w-full max-w-[860px] px-6">
          <h2 className={`${H2} text-center`}>FCA evidence — honesty beat</h2>
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
                a workflow you care about — no slide pitch.
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
              Attestix is an evidence tool, not a guarantor of compliance —
              providers remain liable under EU AI Act Articles 16-22 regardless of
              which evidence tool they use. We do not provide legal advice. Base L2
              anchoring is Sepolia testnet only as of v0.4.1; mainnet schema
              registration is on the roadmap.
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
