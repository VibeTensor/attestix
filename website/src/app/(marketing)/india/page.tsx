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
    body: "Financial-sector teams should assess applicable reporting, outsourcing and audit requirements for their entity and activity. Signed records support review; they do not establish regulatory acceptance.",
  },
  {
    n: "03",
    title: "MeitY AI advisory + IndiaAI Mission",
    body: "AI teams should review applicable official guidance and implementation dates. Attestix provides open-source signed evidence without a conformity or endorsement claim.",
  },
];

const ICPS = [
  {
    city: "Bangalore",
    sector: "Fintech",
    pain: "Trading, payment and fraud workflows may require action records, lineage and reviewed access controls. Requirements depend on the entity and intended use.",
    wedge: "Attestix provides signed identity, delegated authority and hash-chained records. Optional testnet anchoring and operational acceptance require separate review.",
  },
  {
    city: "Mumbai",
    sector: "BFSI",
    pain: "Large bank AI pilots  -  credit scoring, fraud detection, customer-support copilots  -  need explainable provenance and lineage for internal model-risk and external supervisory review.",
    wedge: "Attestix records signed model-lineage and training-data evidence. Generated declarations are provider-review drafts, not conformity determinations.",
  },
  {
    city: "Hyderabad",
    sector: "ML platform teams",
    pain: "Internal ML platforms at large enterprises are accreting governance functions  -  pipeline-step attestation, model-card publishing, agent registry. Build-vs-buy is the live question.",
    wedge: "Attestix provides Python, MCP, CLI and REST interfaces and export bundles within the documented profile. Review authentication, storage and custody before deployment.",
  },
];

const INSTALL_SNIPPET = `# Install Attestix
pip install attestix

# Issue an agent identity
attestix identity create --name research-bot --did-method key

# Log a hash-chained audit event
attestix audit log "tool_call planFlights"

# Check recorded chain continuity and signatures
attestix audit verify-chain`;

export default function IndiaPage() {
  return (
    <>
      <section className="px-6 pb-16 pt-16 text-center md:pt-20">
        <div className="mx-auto max-w-[860px]">
          <AtxEyebrow>Region  /  India</AtxEyebrow>
          <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
            Attestix <span className="text-atx-accent"> /  India.</span>
          </h1>
          <div className="mx-auto mt-5 max-w-[680px] space-y-4 text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
            <p>
              Signed identity and governance evidence for Indian teams evaluating AI agent workflows. Applicable obligations depend on the system, operator role and sector. Use official requirements and implementation dates when assessing a deployment.
            </p>
            <p>
              Attestix provides agent identity, delegated authority and audit records. Optional testnet anchoring requires separate configuration and network access. These records support review; they do not prove complete capture or legal conformity.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-atx-bg-elev py-20">
        <div className={WRAP}>
          <h2 className={`${H2} text-center`}>Why now for India</h2>
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
        <div className={`${WRAP} text-center`}>
          <h2 className={H2}>The DPI parallel</h2>
          <div className="mx-auto mt-10 max-w-[820px] rounded-2xl border border-atx-accent/30 bg-atx-accent/[0.05] p-7 text-left">
            <p className="text-[17px] leading-[1.65] text-atx-ink-mid">
              Signed identities and verifiable records are useful building blocks for agent workflows. Comparisons with public digital infrastructure do not imply government endorsement, interoperability certification or identical security properties.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-atx-bg-elev py-20">
        <div className={WRAP}>
          <h2 className={`${H2} text-center`}>Who Attestix fits in India</h2>
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
                Bring your governance lead, your engineering lead, and whoever
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
              Attestix supplies evidence tooling and managed local record handling. Applicable DPDP and other obligations require separate assessment. Remote copies, retention, data rights, lawful processing and operating controls remain responsibilities of the deploying team.
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
