import Link from "next/link";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "Attestix  /  India",
  description:
    "Signed identity and governance evidence for Indian teams evaluating AI agent workflows. Regulatory applicability requires separate review.",
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
    title: "DPDP Act 2023 + Rules 2025",
    body: "Deploying teams should assess applicable DPDP requirements, roles and implementation dates separately. Attestix provides evidence and managed local record handling; it does not establish DPDP conformity.",
  },
  {
    n: "02",
    title: "RBI Master Direction on IT outsourcing",
    body: "The RBI's Master Direction on IT outsourcing (2023/2024) mandates audit trails for any IT process material to a regulated financial entity  -  including AI-driven trading, credit, and KYC. Attestix's hash-chained audit and on-chain anchor fit the tamper-evident audit-trail requirement cleanly.",
  },
  {
    n: "03",
    title: "MeitY AI advisory + IndiaAI Mission",
    body: "MeitY's revised draft AI advisory pushes traceability and grievance redressal for significant AI deployments. The IndiaAI Mission's safe-and-trusted-AI pillar explicitly names open-source foundational infrastructure  -  Attestix is exactly that, with Apache-2.0 and a published canonical-form spec.",
  },
];

const ICPS = [
  {
    city: "Bangalore",
    sector: "Fintech",
    pain: "Agent-driven trading, payment routing, and fraud monitoring sit under RBI audit-trail requirements. Today most teams cobble together logs in S3 buckets with no signature and no retention proof.",
    wedge: "Attestix issues Ed25519-signed DIDs per agent, UCAN delegations per action, hash-chained audit anchored to Base Sepolia testnet. RBI-readable evidence; UPI-adjacent latencies.",
  },
  {
    city: "Mumbai",
    sector: "BFSI",
    pain: "Large bank AI pilots  -  credit scoring, fraud detection, customer-support copilots  -  need explainable provenance and lineage for internal model-risk and external supervisory review.",
    wedge: "Attestix records model lineage and training-data provenance as W3C Verifiable Credentials, with a declaration-of-conformity generator for high-risk profiles.",
  },
  {
    city: "Hyderabad",
    sector: "ML platform teams",
    pain: "Internal ML platforms at large enterprises are accreting governance functions  -  pipeline-step attestation, model-card publishing, agent registry. Build-vs-buy is the live question.",
    wedge: "Attestix is the build-substrate: MCP tools, 9 service modules, 44 REST endpoints. Self-host with Docker; export bundles for portability under the published wire-format.",
  },
];

const INSTALL_SNIPPET = `# Install Attestix
pip install attestix

# Issue an agent identity
attestix identity create --name research-bot --did-method key

# Log a hash-chained audit event
attestix audit log "tool_call planFlights"

# Verify the chain (any tampering breaks here)
attestix audit verify-chain`;

export default function IndiaPage() {
  return (
    <section className="mx-auto max-w-[1080px] px-7 py-24">
      <AtxEyebrow>Region  /  India</AtxEyebrow>
      <h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
        Attestix
        <br />
        <em className="italic text-atx-accent"> /  India.</em>
      </h1>

      <div className="mt-10 max-w-[760px] space-y-5 text-[15px] leading-[1.65] text-atx-ink-mid">
        <p>
          Signed identity and governance evidence for Indian teams evaluating
          AI agent workflows. Applicable obligations depend on the system,
          operator role and sector. Use the relevant official requirements
          and implementation timetable when assessing a deployment.
        </p>
        <p>
          Attestix provides agent identity, delegated authority and audit
          records. Optional Base L2 testnet anchoring requires separate
          configuration and network access. These records support review;
          they do not prove complete capture or legal conformity.
        </p>
      </div>

      <h2 className="mt-20 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        Why now for India
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
          </div>
        </div>
      </section>

      <h2 className="mt-20 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        The DPI parallel
      </h2>
      <div className="mt-4 max-w-[820px] rounded-atx-md border border-atx-line-soft bg-atx-panel p-7">
        <p className="text-[14.5px] leading-[1.7] text-atx-ink-mid">
          India&apos;s Digital Public Infrastructure is the global gold standard for
          open-source, sovereign, verifiable digital primitives  -  Aadhaar for
          identity, UPI for payments, DigiLocker for credentials, Account
          Aggregator for consented data. Just as DigiLocker is verifiable
          identity infrastructure for citizens,{" "}
          <span className="text-atx-ink">
            Attestix is verifiable identity infrastructure for AI agents
          </span>
          {" "} -  same primitives (signed credentials, public verifiability),
          one layer higher, different subjects. The pitch lands in India
          because the audience already understands the architecture
          intuitively.
        </p>
      </div>

      <section className="bg-atx-bg py-20">
        <div className={`${WRAP} text-center`}>
          <h2 className={H2}>The DPI parallel</h2>
          <div className="mx-auto mt-10 max-w-[820px] rounded-2xl border border-atx-accent/30 bg-atx-accent/[0.05] p-7 text-left">
            <p className="text-[17px] leading-[1.65] text-atx-ink-mid">
              India&apos;s Digital Public Infrastructure is the global gold standard for
              open-source, sovereign, verifiable digital primitives  -  Aadhaar for
              identity, UPI for payments, DigiLocker for credentials, Account
              Aggregator for consented data. Just as DigiLocker is verifiable
              identity infrastructure for citizens,{" "}
              <span className="text-atx-ink">
                Attestix is verifiable identity infrastructure for AI agents
              </span>
              {" "} -  same primitives (signed credentials, public verifiability),
              one layer higher, different subjects. The pitch lands in India
              because the audience already understands the architecture
              intuitively.
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
        About VibeTensor
      </h2>
      <div className="mt-4 max-w-[820px] rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-6">
        <p className="text-[13.5px] leading-[1.7] text-atx-ink-mid">
          Attestix is built by{" "}
          <span className="text-atx-ink">VibeTensor Private Limited</span>,
          India-incorporated (registered office Warangal, Telangana; CIN{" "}
          <code className="rounded-atx-xs border border-atx-line-soft bg-atx-panel px-1.5 py-0.5 font-mono-atx text-[11.5px] text-atx-accent">
            U74909TS2025PTC197692
          </code>
          ), operating from Bengaluru. We model on India&apos;s DPI playbook  -
          open standards, sovereign deployability, custom data residency on
          the Enterprise tier when that conversation begins.
        </p>
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
        {" "} -  LangChain, OpenAI Agents SDK, and CrewAI are real integrations
        (not example shims). Dify, Google ADK, Semantic Kernel, and Strands are
        example-only via the MCP server.
      </p>

      <section className="bg-atx-bg py-20">
        <div className="mx-auto w-full max-w-[860px] px-6">
          <h2 className={`${H2} text-center`}>About VibeTensor</h2>
          <div className="mt-10 rounded-2xl border border-atx-line bg-atx-panel/60 p-6">
            <p className="text-[15px] leading-[1.7] text-atx-ink-mid">
              Attestix is built by{" "}
              <span className="text-atx-ink">VibeTensor Private Limited</span>,
              India-incorporated (registered office Warangal, Telangana; CIN{" "}
              <code className="rounded-md border border-atx-line-soft bg-atx-bg-sunken px-1.5 py-0.5 font-mono-atx text-[12.5px] text-atx-accent">
                U74909TS2025PTC197692
              </code>
              ), operating from Bengaluru. We model on India&apos;s DPI playbook  -
              open standards, sovereign deployability, custom data residency on
              the Enterprise tier when that conversation begins.
            </p>
          </div>
          <p className="mt-4 text-[13.5px] leading-[1.6] text-atx-ink-mid">
            Bring your compliance lead, your AI engineering lead, and whoever
            needs to say yes. We will walk through the console end-to-end
            against a workflow you care about  -  no slide pitch.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              href="/demo-call?region=india"
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
        <div className={WRAP}>
          <h2 className={`${H2} text-center`}>Talk to a human</h2>
          <div className="mx-auto mt-12 grid max-w-[1040px] gap-5 md:grid-cols-[1.4fr_1fr]">
            <div className="rounded-2xl border border-atx-line bg-atx-panel p-8">
              <h3 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
                Book a 30-min walkthrough
              </h3>
              <p className="mt-3 text-[15px] leading-[1.6] text-atx-ink-mid">
                Bring your compliance lead, your AI engineering lead, and whoever
                needs to say yes. We will walk through the console end-to-end
                against a workflow you care about  -  no slide pitch.
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <Link
                  href="/demo-call?region=india"
                  className="inline-flex items-center gap-2 rounded-full bg-atx-accent px-6 py-3 text-[15px] font-medium text-[oklch(0.14_0.01_180)] transition-colors duration-200 hover:bg-atx-accent-deep"
                >
                  Book a demo &rarr;
                </Link>
                <a
                  href="mailto:pkd@vibetensor.com?subject=%5BIndia%5D%20Attestix%20demo&body=Company%3A%20%0ARole%3A%20%0AFrameworks%20in%20use%3A%20%0ARisk%20tier%3A%20%0ATimeline%3A%20"
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
              DPDP Act coverage is referenced in our roadmap; it is{" "}
              <span className="text-atx-ink-mid">not yet implemented in v0.4.1</span>  -
              planned for v0.5, ahead of the 14 May 2027 substantive-duties date.
              Attestix is an evidence tool, not a guarantor of compliance:
              providers remain liable under EU AI Act Articles 16-22, and under
              DPDP under the data-fiduciary obligations of the data principal once
              enforced. We do not provide legal advice. Base L2 anchoring is
              Sepolia testnet only; mainnet schema registration is on the roadmap.
            </p>
          </div>
        </div>
        <p className="mt-3 text-[12.5px] leading-[1.6] text-atx-ink-mid">
          The current release provides evidence tooling and managed local
          record handling. It does not establish DPDP or EU AI Act conformity.
          Operators must separately assess lawful data handling, retention,
          external copies and applicable obligations. Base L2 anchoring defaults
          to Base Sepolia and supports Base mainnet when configured. External
          deployment and schema registration require separate verification.
        </p>
      </div>
    </section>
  );
}
