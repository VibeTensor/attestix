import Link from "next/link";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "Attestix · United Kingdom",
  description:
    "AI-Act-grade evidence for UK builders selling into the EU + an FCA-aligned audit story for regulated AI. FCA, ICO, Bank of England framings.",
});

const WHY_NOW = [
  {
    n: "01",
    title: "EU AI Act extraterritoriality",
    body: "UK firms selling AI services into the EU are providers or deployers under Articles 25 and 28. The Act enters general application on 2 August 2026 — a UK-incorporated supplier with EU customers carries the obligations regardless of where the team sits.",
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
    <section className="mx-auto max-w-[1080px] px-7 py-24">
      <AtxEyebrow>Region · United Kingdom</AtxEyebrow>
      <h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
        Attestix
        <br />
        <em className="italic text-atx-accent">· United Kingdom.</em>
      </h1>

      <div className="mt-10 max-w-[760px] space-y-5 text-[15px] leading-[1.65] text-atx-ink-mid">
        <p>
          AI-Act-grade evidence for UK builders selling into the EU, and an
          FCA-aligned audit story for regulated AI. The UK is consciously
          <em> not </em>
          mirroring the EU horizontal regulation; each sector regulator (FCA,
          MHRA, Ofcom, ICO) brings AI rules into existing frameworks. UK firms
          exporting AI services to the EU still have to clear 2 August 2026 —
          so the UK market gets two regulatory regimes for the price of one.
        </p>
        <p>
          Attestix is the open-source identity, audit, and on-chain anchoring
          layer that gives AI agents the equivalent of a passport. The
          cryptographic primitives are sector-neutral, so the same evidence
          trail works under both regimes.
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
            <p className="mt-4 text-[13px] leading-[1.6] text-atx-ink-mid">
              <span className="font-mono-atx text-[10.5px] uppercase tracking-[0.12em] text-atx-ink-faint">
                Wedge
              </span>
              <br />
              {icp.wedge}
            </p>
          </article>
        ))}
      </div>

      <h2 className="mt-20 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        What you can do in 90 seconds
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
        {" "}— LangChain, OpenAI Agents SDK, and CrewAI are real integrations
        (not example shims). Dify, Google ADK, Semantic Kernel, and Strands are
        example-only via the MCP server.
      </p>

      <h2 className="mt-20 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        FCA evidence — honesty beat
      </h2>
      <div className="mt-4 rounded-atx-md border border-atx-line-soft bg-atx-panel p-6 text-[13.5px] leading-[1.65] text-atx-ink-mid">
        <p>
          Attestix is a single-maintainer beta with 15 GitHub stars and no
          independent third-party security audit as of v0.4.1. Open-source
          signing keys live as filesystem-mode-0600 JSON; there is no HSM/KMS
          backend in the OSS engine today.
        </p>
        <p className="mt-4">
          That is enough for staging, internal copilots, and pre-production
          governance pilots. For an FCA-regulated production-of-record
          deployment, the Cloud Enterprise tier (BYOK against AWS KMS Frankfurt,
          FIPS 140-2 L3) is the bridge. We name this gap because regulated UK
          buyers will ask, and an evidence tool that hides its own threat model
          fails the first audit it meets.
        </p>
      </div>

      <h2 className="mt-20 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        Talk to a human
      </h2>
      <div className="mt-6 grid gap-6 md:grid-cols-[1.4fr_1fr]">
        <div className="rounded-atx-md border border-atx-line-soft bg-atx-panel p-7">
          <div className="font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
            Book a 30-min walkthrough
          </div>
          <p className="mt-4 text-[13.5px] leading-[1.6] text-atx-ink-mid">
            Bring your compliance lead, your AI engineering lead, and whoever
            needs to say yes. We will walk through the console end-to-end against
            a workflow you care about — no slide pitch.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              href="/demo-call?region=uk"
              className="inline-flex h-10 items-center gap-2 rounded-atx-md bg-atx-accent px-5 text-[13px] font-medium text-[oklch(0.14_0.01_180)] transition-colors hover:bg-atx-accent-deep"
            >
              Book a demo →
            </Link>
            <a
              href="mailto:pkd@vibetensor.com?subject=%5BUK%5D%20Attestix%20demo&body=Company%3A%20%0ARole%3A%20%0AFrameworks%20in%20use%3A%20%0ARisk%20tier%3A%20%0ATimeline%3A%20"
              className="inline-flex h-10 items-center rounded-atx-md border border-atx-line px-5 text-[13px] font-medium text-atx-ink transition-colors hover:border-atx-ink-dim hover:bg-atx-bg-sunken"
            >
              Email pkd@vibetensor.com
            </a>
          </div>
        </div>
        <div className="rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-6">
          <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
            Not ready for a call?
          </div>
          <ul className="mt-3 space-y-2 text-[13px] leading-[1.55] text-atx-ink-mid">
            <li>
              Try the{" "}
              <Link href="/console" className="text-atx-accent hover:underline">
                interactive console
              </Link>
            </li>
            <li>
              Read the{" "}
              <Link href="/docs" className="text-atx-accent hover:underline">
                docs
              </Link>
            </li>
            <li>
              Star the repo on{" "}
              <a
                href="https://github.com/VibeTensor/attestix"
                target="_blank"
                rel="noopener noreferrer"
                className="text-atx-accent hover:underline"
              >
                GitHub
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div className="mt-16 rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-6">
        <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
          Compliance posture
        </div>
        <p className="mt-3 text-[12.5px] leading-[1.6] text-atx-ink-mid">
          Attestix is an evidence tool, not a guarantor of compliance —
          providers remain liable under EU AI Act Articles 16-22 regardless of
          which evidence tool they use. We do not provide legal advice. Base L2
          anchoring is Sepolia testnet only as of v0.4.1; mainnet schema
          registration is on the roadmap.
        </p>
      </div>
    </section>
  );
}
