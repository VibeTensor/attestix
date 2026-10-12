import Link from "next/link";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "Attestix / United Kingdom",
  description:
    "Signed identity and governance evidence for UK teams evaluating AI agent workflows. Legal and regulatory applicability requires separate review.",
});

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
            a workflow you care about  -  no slide pitch.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              href="/demo-call?region=uk"
              className="inline-flex h-10 items-center gap-2 rounded-atx-md bg-atx-accent px-5 text-[13px] font-medium text-[oklch(0.14_0.01_180)] transition-colors hover:bg-atx-accent-deep"
            >
              Book a demo -&gt;
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
          Attestix is an evidence tool, not a guarantor of compliance  -
          applicable duties depend on the system, operator role and
          jurisdiction. We do not provide legal advice. Testnet anchoring does
          not establish production availability or regulatory acceptance.
        </p>
      </div>
    </section>
  );
}
