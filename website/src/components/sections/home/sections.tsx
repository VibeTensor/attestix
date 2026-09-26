import Link from "next/link";
import { ArrowRight, KeyRound, ListOrdered, ShieldCheck } from "lucide-react";
import { AtxCopyText } from "@/components/atx/atx-copy-text";
import { ATX_HERO_STATS } from "@/lib/atx-data";
import { siteConfig } from "@/lib/config";

const WRAP = "mx-auto w-full max-w-[1200px] px-6";
const H2 = "text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink";
const LEAD = "text-[17.5px] leading-[1.6] text-atx-ink-mid";

// Only integrations that ship in the package or are independently verifiable.
const WORKS_WITH = [
  { name: "LangChain", href: "/docs/guides/langchain" },
  { name: "CrewAI", href: "/docs/guides/crewai" },
  { name: "OpenAI Agents SDK", href: "/docs/guides/openai-agents-sdk" },
  { name: "Claude Code (MCP)", href: "/docs/getting-started" },
];

function TextLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className="group inline-flex items-center gap-1.5 text-[14px] font-medium text-atx-ink-mid underline decoration-atx-line underline-offset-4 transition-colors duration-200 hover:text-atx-ink hover:decoration-atx-ink-dim"
    >
      {children}
      <ArrowRight className="h-3.5 w-3.5 transition-transform duration-200 group-hover:translate-x-0.5" />
    </Link>
  );
}

export function HomeHero() {
  return (
    <section className="relative px-6 pb-10 pt-16 text-center md:pt-20">
      <div className="relative mx-auto max-w-[860px]">
        <h1 className="text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
          <span className="text-atx-accent">Cryptographic proof</span> your AI agents
          are compliant
        </h1>
        <p className={`mx-auto mt-5 max-w-[640px] [text-wrap:balance] ${LEAD}`}>
          Attestix gives every AI agent a verifiable identity and a tamper-evident
          audit trail: open-source evidence a regulator, auditor, or another agent
          can check for itself.
        </p>
        <Link
          href="/console"
          className="mt-8 inline-flex rounded-full bg-atx-accent px-8 py-3.5 text-[15px] font-medium text-[oklch(0.14_0.01_180)] transition-colors duration-200 hover:bg-atx-accent-deep"
        >
          Try the console demo
        </Link>
      </div>

      <div className="mx-auto mt-12 max-w-[860px] border-t border-atx-line-soft pt-7">
        <p className="text-[15px] text-atx-ink-mid">Works with the agent stack you already use</p>
        <div className="mt-4 flex flex-wrap items-center justify-center gap-x-9 gap-y-3">
          {WORKS_WITH.map((w) => (
            <Link
              key={w.name}
              href={w.href}
              className="text-[17px] font-medium tracking-[-0.01em] text-atx-ink-dim transition-colors duration-200 hover:text-atx-ink"
            >
              {w.name}
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

const TINT = {
  gold: { card: "border-atx-accent/30 bg-atx-accent/[0.05]", chip: "bg-atx-accent/15 text-atx-accent" },
  info: { card: "border-atx-info/30 bg-atx-info/[0.05]", chip: "bg-atx-info/15 text-atx-info" },
  ok: { card: "border-atx-ok/30 bg-atx-ok/[0.05]", chip: "bg-atx-ok/15 text-atx-ok" },
} as const;

function FlowCard({
  tint,
  icon,
  title,
  children,
  body,
}: {
  tint: keyof typeof TINT;
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
  body: string;
}) {
  return (
    <div className={`rounded-2xl border p-[18px] text-left ${TINT[tint].card}`}>
      <div className="flex items-center gap-3">
        <span className={`grid h-10 w-10 place-items-center rounded-xl ${TINT[tint].chip}`}>{icon}</span>
        <h3 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">{title}</h3>
      </div>
      <div className="mt-4 rounded-xl border border-atx-line-soft bg-atx-bg-sunken/70 px-3 py-2.5 font-mono-atx text-[12px] leading-[1.7]">
        {children}
      </div>
      <p className="mt-3.5 text-[14px] leading-[1.55] text-atx-ink-mid">{body}</p>
    </div>
  );
}

export function HomeHow() {
  return (
    <section id="how-it-works" className="scroll-mt-20 bg-atx-bg py-20">
      <div className={`${WRAP} text-center`}>
        <h2 className={H2}>How Attestix works</h2>
        <p className={`mt-3 ${LEAD}`}>One identity per agent. Evidence anyone can check.</p>

        <div className="mx-auto mt-12 grid max-w-[1040px] items-center gap-5 lg:grid-cols-[1fr_minmax(0,300px)_1fr] lg:gap-0">
          <div className="lg:col-start-2">
            <FlowCard
              tint="gold"
              icon={<KeyRound className="h-5 w-5" />}
              title="Issue an identity"
              body="Give each agent a DID and a signed identity before it takes its first action."
            >
              <div className="text-atx-ink-dim">$ attestix init --name quarterly-analyst</div>
              <div className="truncate text-atx-accent">did:key:z6Mkfz1de3keHmij4P5B...</div>
            </FlowCard>
          </div>

          <div aria-hidden className="mx-auto hidden h-10 w-px bg-atx-line lg:col-start-2 lg:block" />

          <div className="lg:col-start-1 lg:row-start-3 lg:pr-6">
            <FlowCard
              tint="info"
              icon={<ListOrdered className="h-5 w-5" />}
              title="Record every action"
              body="Tool calls land in a hash-chained audit trail that shows exactly where it was altered."
            >
              <div className="text-atx-ink-dim">#9c1e &rarr; #4a7b &rarr; #e03d</div>
              <div className="text-atx-ok">chain intact &middot; 3 of 3 linked</div>
            </FlowCard>
          </div>

          <div className="relative lg:col-start-2 lg:row-start-3">
            <span aria-hidden className="absolute -left-6 top-1/2 hidden w-6 border-t border-dashed border-atx-line lg:block" />
            <span aria-hidden className="absolute -right-6 top-1/2 hidden w-6 border-t border-dashed border-atx-line lg:block" />
            <div className="rounded-2xl border border-atx-line bg-atx-panel p-4 text-left">
              <p className="text-[13px] font-medium text-atx-ink">Your AI agents</p>
              <div className="mt-3 grid grid-cols-2 gap-2">
                {["LangChain", "CrewAI", "OpenAI Agents", "Claude Code"].map((a) => (
                  <div
                    key={a}
                    className="rounded-lg border border-atx-line-soft bg-atx-bg-sunken px-2 py-3 text-center text-[12px] font-medium text-atx-ink-mid"
                  >
                    {a}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="lg:col-start-3 lg:row-start-3 lg:pl-6">
            <FlowCard
              tint="ok"
              icon={<ShieldCheck className="h-5 w-5" />}
              title="Verify anywhere"
              body="Check credentials offline in Python, Go, Rust, Java, JavaScript, or R. Nothing is uploaded."
            >
              <div className="text-atx-ink">attestix:addc20ca69bc4c93 is VALID</div>
              <div className="text-atx-ok">signature_valid: PASS</div>
            </FlowCard>
          </div>
        </div>

        <div className="mt-10">
          <TextLink href="/platform">See the full platform</TextLink>
        </div>
      </div>
    </section>
  );
}

export function HomeResults() {
  const [lead, ...rest] = ATX_HERO_STATS;
  return (
    <section className="bg-atx-bg-elev pt-20">
      <div className={WRAP}>
        <h2 className={`${H2} text-center`}>
          Evidence that holds up.
          <br />
          No call home required.
        </h2>
        <div className="mt-12 grid border-y border-atx-line-soft md:grid-cols-[1.4fr_1fr_1fr_1fr]">
          <div className="px-7 py-8">
            <div className="text-[88px] font-normal leading-none tracking-[-0.04em] text-atx-accent">{lead.v}</div>
            <div className="mt-3 text-[22px] leading-[1.3] text-atx-accent">{lead.k}</div>
          </div>
          {rest.map((s) => (
            <div key={s.k} className="border-t border-atx-line-soft px-7 py-8 md:border-l md:border-t-0">
              <div className="text-[40px] leading-none tracking-[-0.03em] text-atx-accent">{s.v}</div>
              <div className="mt-3 text-[14px] leading-[1.45] text-atx-ink-mid">{s.k}</div>
            </div>
          ))}
        </div>
        <p className="mx-auto mt-6 max-w-[720px] text-center text-[13px] leading-[1.6] text-atx-ink-dim">
          Tool count read from source. Verifiers in six languages share one set of
          test vectors. The browser verifier at /verify uploads nothing. Apache 2.0:
          self-host free, forever.
        </p>

        <Link
          href="/changelog"
          className="group mx-auto mt-8 flex max-w-[840px] items-center justify-between rounded-xl border border-atx-line bg-atx-bg-elev px-7 py-6 transition-colors duration-200 hover:border-atx-ink-dim"
        >
          <span>
            <span className="block text-[14px] text-atx-accent">What&rsquo;s new</span>
            <span className="mt-1 block text-[26px] tracking-[-0.6px] text-atx-ink">
              Attestix v{siteConfig.version} release notes
            </span>
          </span>
          <span className="grid h-10 w-10 place-items-center rounded-full border border-atx-accent/60 text-atx-accent transition-transform duration-200 group-hover:translate-x-0.5">
            <ArrowRight className="h-4 w-4" />
          </span>
        </Link>
        <div className="mt-20 border-t border-atx-line-soft" />
      </div>
    </section>
  );
}

const STANDARDS = [
  {
    name: "W3C Verifiable Credentials",
    body: "Credentials use the W3C VC 1.1 data model, a shape wallets and verifiers already understand.",
    href: "https://www.w3.org/TR/vc-data-model/",
  },
  {
    name: "W3C Decentralized Identifiers",
    body: "Agents are named by did:key and did:web identifiers that resolve without Attestix in the loop.",
    href: "https://www.w3.org/TR/did-core/",
  },
  {
    name: "IETF Ed25519 and Merkle hashing",
    body: "Ed25519 signatures (RFC 8032) and RFC 6962 leaf and node hashing, with optional anchoring on Base via EAS.",
    href: "https://www.rfc-editor.org/rfc/rfc8032",
  },
];

export function HomeStandards() {
  return (
    <section className="bg-atx-bg-elev py-20">
      <div className={`${WRAP} text-center`}>
        <h2 className={H2}>Built on open standards</h2>
        <p className={`mx-auto mt-4 max-w-[760px] ${LEAD}`}>
          Attestix builds on published specifications rather than a private format,
          so the evidence outlives any one vendor, including us.
        </p>
        <div className="mt-12 grid border-t border-atx-line-soft text-left md:grid-cols-3">
          {STANDARDS.map((s, i) => (
            <a
              key={s.name}
              href={s.href}
              target="_blank"
              rel="noopener noreferrer"
              className={`group px-7 py-8 transition-colors duration-200 hover:bg-atx-panel/40 ${i ? "border-t border-atx-line-soft md:border-l md:border-t-0" : ""}`}
            >
              <h3 className="text-[21px] tracking-[-0.4px] text-atx-ink">{s.name}</h3>
              <p className="mt-3 text-[15px] leading-[1.6] text-atx-ink-mid">{s.body}</p>
              <span className="mt-5 inline-block text-[13px] text-atx-ink-dim transition-colors duration-200 group-hover:text-atx-accent">
                Read the specification &#8599;
              </span>
            </a>
          ))}
        </div>
        <Link
          href="/research"
          className="mt-10 inline-flex items-center gap-2 rounded-full border border-atx-line px-6 py-3 text-[14px] font-medium text-atx-ink-mid transition-colors duration-200 hover:border-atx-ink-dim hover:text-atx-ink"
        >
          Read the research <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>
    </section>
  );
}

const INSTALL = `pip install attestix
attestix init --name my-agent
attestix verify <agent-id>`;

export function HomeInstall() {
  return (
    <section className="bg-atx-bg px-6 pt-20">
      <div className="mx-auto max-w-[1120px] rounded-2xl border border-atx-line bg-atx-panel/60 px-6 py-16 text-center">
        <h2 className={H2}>Install Attestix</h2>
        <p className={`mt-4 ${LEAD}`}>
          Open source. Runs as a Python library, a CLI, or an MCP server.
        </p>
        <div className="relative mx-auto mt-9 max-w-[560px] rounded-xl bg-atx-bg-sunken p-6 text-left font-mono-atx text-[13px] leading-[1.9]">
          <AtxCopyText
            value={INSTALL}
            title="Copy commands"
            className="absolute right-3 top-3 rounded-lg border border-atx-line px-2.5 py-1 text-[11px] text-atx-ink-dim transition-colors duration-150 hover:border-atx-accent hover:text-atx-accent"
          >
            copy
          </AtxCopyText>
          <div><span className="text-atx-accent">$</span> <span className="text-atx-ink">pip install</span> <span className="text-atx-ok">attestix</span></div>
          <div className="text-atx-ink-faint"># create a signed identity for an agent</div>
          <div><span className="text-atx-accent">$</span> <span className="text-atx-ink">attestix init</span> <span className="text-atx-info">--name</span> my-agent</div>
          <div><span className="text-atx-accent">$</span> <span className="text-atx-ink">attestix verify</span> <span className="text-atx-ink-dim">&lt;agent-id&gt;</span></div>
        </div>
        <div className="mt-8">
          <TextLink href="/docs/getting-started">Setup documentation</TextLink>
        </div>
      </div>
    </section>
  );
}

const FAQ_PICK = [
  "What is Attestix?",
  "Does Attestix work with LangChain, OpenAI Agents SDK, or CrewAI?",
  "Can I use Attestix without blockchain?",
  "What is the current maturity level?",
];

export function HomeFaq() {
  const items = FAQ_PICK.map((q) => siteConfig.faq.find((f) => f.question === q)).filter(
    (f): f is (typeof siteConfig.faq)[number] => Boolean(f),
  );
  return (
    <section className="bg-atx-bg px-6 py-16">
      <p className="text-center text-[14px] font-medium tracking-[0.08em] text-atx-ink-mid">FAQ</p>
      <div className="mx-auto mt-6 max-w-[720px] rounded-xl border border-atx-line bg-atx-panel/60 px-6">
        {items.map((f, i) => (
          <details key={f.question} className={`group ${i ? "border-t border-atx-line-soft" : ""}`}>
            <summary className="flex cursor-pointer list-none items-center gap-3 py-5 text-[15px] font-medium text-atx-ink transition-colors duration-150 hover:text-atx-accent">
              <span className="text-atx-ink-dim transition-transform duration-150 group-open:rotate-90">&rsaquo;</span>
              {f.question}
            </summary>
            <p className="pb-5 pl-6 text-[15px] leading-[1.65] text-atx-ink-mid">{f.answer}</p>
          </details>
        ))}
      </div>
      <div className="mt-6 text-center">
        <TextLink href="/faq">All questions</TextLink>
      </div>
    </section>
  );
}

export function HomeTalk() {
  return (
    <section className="relative overflow-hidden py-20">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(720px 100% at 50% 100%, color-mix(in oklch, var(--color-atx-accent) 11%, transparent), transparent 100%)",
        }}
      />
      <div className={`${WRAP} relative grid items-center gap-10 md:grid-cols-2`}>
        <div>
          <p className="text-[14px] text-atx-accent">30-minute call</p>
          <h2 className="mt-3 text-[44px] font-medium leading-[1.12] tracking-[-1.1px] text-atx-ink">
            See how Attestix fits your agents
          </h2>
          <p className={`mt-5 max-w-[440px] ${LEAD}`}>
            Talk through your agents, their risk tier, and the evidence your auditors
            will ask for.
          </p>
          <div className="mt-6">
            <TextLink href="/demo/fine-calculator">Estimate your EU AI Act exposure</TextLink>
          </div>
        </div>
        <div className="rounded-2xl border border-atx-line bg-atx-panel p-8">
          <p className="text-[15px] leading-[1.6] text-atx-ink-mid">
            Pick a slot on the calendar that suits your team.
          </p>
          <a
            href="https://cal.com/vibetensor/attestix"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-6 flex w-full items-center justify-center gap-2 rounded-full bg-white px-6 py-3.5 text-[15px] font-medium text-[#111315] transition-shadow duration-200 hover:shadow-[0_8px_30px_rgba(230,172,61,0.3)]"
          >
            Book a call <span aria-hidden>&#8599;</span>
          </a>
          <p className="mt-5 text-center text-[13px] text-atx-ink-dim">
            or email{" "}
            <a href="mailto:info@vibetensor.com" className="underline underline-offset-4 hover:text-atx-ink">
              info@vibetensor.com
            </a>
          </p>
        </div>
      </div>
    </section>
  );
}
