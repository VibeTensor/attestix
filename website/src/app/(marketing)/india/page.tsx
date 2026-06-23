import Link from "next/link";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "Attestix · India",
  description:
    "DPDP-aware AI infrastructure for Indian builders + an RBI-readable audit story for fintech and BFSI. DPDP Act 2023, RBI Master Direction, MeitY AI advisory framings.",
});

const WHY_NOW = [
  {
    n: "01",
    title: "DPDP Act 2023 + Rules 2025",
    body: "Notified 14 November 2025; substantive duties — notice, consent, data-principal rights, Consent Manager, breach notification — land on 14 May 2027. Today Attestix has zero DPDP-specific code; this is referenced in our roadmap, not shipped in v0.4.1.",
  },
  {
    n: "02",
    title: "RBI Master Direction on IT outsourcing",
    body: "The RBI's Master Direction on IT outsourcing (2023/2024) mandates audit trails for any IT process material to a regulated financial entity — including AI-driven trading, credit, and KYC. Attestix's hash-chained audit and on-chain anchor fit the tamper-evident audit-trail requirement cleanly.",
  },
  {
    n: "03",
    title: "MeitY AI advisory + IndiaAI Mission",
    body: "MeitY's revised draft AI advisory pushes traceability and grievance redressal for significant AI deployments. The IndiaAI Mission's safe-and-trusted-AI pillar explicitly names open-source foundational infrastructure — Attestix is exactly that, with Apache-2.0 and a published canonical-form spec.",
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
    pain: "Large bank AI pilots — credit scoring, fraud detection, customer-support copilots — need explainable provenance and lineage for internal model-risk and external supervisory review.",
    wedge: "Attestix records model lineage and training-data provenance as W3C Verifiable Credentials, with a declaration-of-conformity generator for high-risk profiles.",
  },
  {
    city: "Hyderabad",
    sector: "ML platform teams",
    pain: "Internal ML platforms at large enterprises are accreting governance functions — pipeline-step attestation, model-card publishing, agent registry. Build-vs-buy is the live question.",
    wedge: "Attestix is the build-substrate: 47 MCP tools, 9 service modules, 44 REST endpoints. Self-host with Docker; export bundles for portability under the published wire-format.",
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

export default function IndiaPage() {
  return (
    <section className="mx-auto max-w-[1080px] px-7 py-24">
      <AtxEyebrow>Region · India</AtxEyebrow>
      <h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
        Attestix
        <br />
        <em className="italic text-atx-accent">· India.</em>
      </h1>

      <div className="mt-10 max-w-[760px] space-y-5 text-[15px] leading-[1.65] text-atx-ink-mid">
        <p>
          DPDP-aware AI infrastructure for Indian builders, and an
          RBI-readable audit story for fintech and BFSI. India just notified
          the DPDP Rules — substantive duties land on 14 May 2027 — and the
          RBI&apos;s Master Direction on IT outsourcing already wants audit trails
          for AI-driven trading and credit decisions.
        </p>
        <p>
          Attestix is the open-source identity, audit, and on-chain anchoring
          layer that gives every AI agent a verifiable credential, a UCAN
          delegation chain for every action, and a hash-chained audit anchored
          to Base L2 (Sepolia testnet today; mainnet planned).
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
          </article>
        ))}
      </div>

      <h2 className="mt-20 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        The DPI parallel
      </h2>
      <div className="mt-4 max-w-[820px] rounded-atx-md border border-atx-line-soft bg-atx-panel p-7">
        <p className="text-[14.5px] leading-[1.7] text-atx-ink-mid">
          India&apos;s Digital Public Infrastructure is the global gold standard for
          open-source, sovereign, verifiable digital primitives — Aadhaar for
          identity, UPI for payments, DigiLocker for credentials, Account
          Aggregator for consented data. Just as DigiLocker is verifiable
          identity infrastructure for citizens,{" "}
          <span className="text-atx-ink">
            Attestix is verifiable identity infrastructure for AI agents
          </span>
          {" "}— same primitives (signed credentials, public verifiability),
          one layer higher, different subjects. The pitch lands in India
          because the audience already understands the architecture
          intuitively.
        </p>
      </div>

      <h2 className="mt-20 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        Who Attestix fits in India
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
          ), operating from Bengaluru. We model on India&apos;s DPI playbook —
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
        {" "}— LangChain, OpenAI Agents SDK, and CrewAI are real integrations
        (not example shims). Dify, Google ADK, Semantic Kernel, and Strands are
        example-only via the MCP server.
      </p>

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
            needs to say yes. We will walk through the console end-to-end
            against a workflow you care about — no slide pitch.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              href="/demo-call?region=india"
              className="inline-flex h-10 items-center gap-2 rounded-atx-md bg-atx-accent px-5 text-[13px] font-medium text-[oklch(0.14_0.01_180)] transition-colors hover:bg-atx-accent-deep"
            >
              Book a demo →
            </Link>
            <a
              href="mailto:pkd@vibetensor.com?subject=%5BIndia%5D%20Attestix%20demo&body=Company%3A%20%0ARole%3A%20%0AFrameworks%20in%20use%3A%20%0ARisk%20tier%3A%20%0ATimeline%3A%20"
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
          DPDP Act coverage is referenced in our roadmap; it is{" "}
          <span className="text-atx-ink">not yet implemented in v0.4.1</span> —
          planned for v0.5, ahead of the 14 May 2027 substantive-duties date.
          Attestix is an evidence tool, not a guarantor of compliance:
          providers remain liable under EU AI Act Articles 16-22, and under
          DPDP under the data-fiduciary obligations of the data principal once
          enforced. We do not provide legal advice. Base L2 anchoring is
          Sepolia testnet only; mainnet schema registration is on the roadmap.
        </p>
      </div>
    </section>
  );
}
