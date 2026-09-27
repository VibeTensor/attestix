import Link from "next/link";
import { ArrowRight, Check, FileSignature, Link2, Radio, ShieldCheck, X } from "lucide-react";
import { ModulesSection } from "@/components/sections/v2/modules";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "Platform",
  description:
    "One evidence layer for every AI agent: capture actions from agent frameworks, MCP clients, and coding agents, sign and hash-chain them, and verify the record anywhere. Open-source core, Attestix Pro, and Attestix Cloud (in development).",
});

const WRAP = "mx-auto w-full max-w-[1200px] px-6";
const H2 = "text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink";
const LEAD = "text-[17.5px] leading-[1.6] text-atx-ink-mid";
const EYEBROW = "text-[14px] font-medium text-atx-accent";
const PILL_PRIMARY =
  "inline-flex items-center gap-2 rounded-full bg-atx-accent px-7 py-3 text-[15px] font-medium text-[oklch(0.14_0.01_180)] transition-colors duration-200 hover:bg-atx-accent-deep";
const PILL_GHOST =
  "inline-flex items-center gap-2 rounded-full border border-atx-line px-6 py-3 text-[15px] font-medium text-atx-ink-mid transition-colors duration-200 hover:border-atx-ink-dim hover:text-atx-ink";

const TINT = {
  gold: { card: "border-atx-accent/30 bg-atx-accent/[0.05]", chip: "bg-atx-accent/15 text-atx-accent" },
  info: { card: "border-atx-info/30 bg-atx-info/[0.05]", chip: "bg-atx-info/15 text-atx-info" },
  ok: { card: "border-atx-ok/30 bg-atx-ok/[0.05]", chip: "bg-atx-ok/15 text-atx-ok" },
} as const;

const STEPS = [
  {
    tint: "gold",
    icon: <Radio className="h-5 w-5" />,
    title: "Capture",
    body: "Framework callbacks, MCP tool calls, the Python API, the REST API, or Pro coding-agent capture record what each agent did.",
  },
  {
    tint: "info",
    icon: <Link2 className="h-5 w-5" />,
    title: "Sign and chain",
    body: "Each record is signed with Ed25519 and hash-chained to the one before it, so an edited, removed, or reordered record breaks the chain.",
  },
  {
    tint: "ok",
    icon: <ShieldCheck className="h-5 w-5" />,
    title: "Verify anywhere",
    body: "Export a bundle and check it offline with the verifier SDKs, the CLI, or the browser verifier, without calling Attestix.",
  },
] as const;

const RUNS_ON = [
  {
    title: "Agent frameworks",
    body: "Shipped helpers in the package: AttestixCallback for LangChain, AttestixAuditHook for the OpenAI Agents SDK, and AttestixCrewAdapter for CrewAI.",
    href: "/docs/guides/integration-guide",
    link: "Integration guide",
  },
  {
    title: "Any MCP client",
    body: "A stdio MCP server exposes all 47 tools to any client that can launch one. Example scripts for more frameworks live in the repository.",
    href: "/docs/reference/mcp-tools",
    link: "MCP tool reference",
  },
  {
    title: "Coding agents",
    body: "Attestix Pro captures Claude Code sessions today. Cursor, Codex CLI, GitHub Copilot, Gemini, and other coding agents are on the roadmap.",
    href: "#coding-agents",
    link: "Coding-agent capture",
  },
  {
    title: "Your own agents",
    body: "Call the Python API directly, or run the REST API (the api extra) and send records from any language over HTTP.",
    href: "/docs/reference/api-reference",
    link: "API reference",
  },
];

type Cell = boolean | string;
const EDITIONS = ["Open source", "Attestix Pro", "Attestix Cloud"] as const;
const COMPARE: { row: string; cells: [Cell, Cell, Cell] }[] = [
  { row: "Status", cells: ["Available (v0.4.1)", "Early access", "In development"] },
  { row: "License", cells: ["Apache 2.0", "Commercial", "Commercial"] },
  { row: "Agent identity, credentials, delegation", cells: [true, true, true] },
  { row: "Hash-chained, signed audit trail", cells: [true, true, true] },
  { row: "EU AI Act records and export bundle", cells: [true, true, true] },
  { row: "Framework integrations, MCP server, CLI, Python API", cells: [true, true, true] },
  { row: "Coding-agent capture and gap detection", cells: [false, true, "Planned"] },
  { row: "Policy enforcement that blocks and records", cells: [false, true, "Planned"] },
  { row: "Hosted ingest and dashboard", cells: [false, false, "Planned"] },
  { row: "Per-tenant signing keys in a KMS", cells: [false, false, "Planned"] },
  { row: "Independent witnessing (RFC 3161, transparency log)", cells: [false, false, "Planned"] },
  { row: "Retention of at least six months", cells: [false, false, "Planned"] },
];

const DETECTS = [
  ["Edited record", "The hash chain breaks at the changed entry."],
  ["Deleted record", "The chain has a missing link."],
  ["Truncated log", "Cutting the end of the log is reported."],
  ["Blocked action", "A denied tool call is recorded as a denial, not dropped."],
];

const PROVES = [
  "The records were not changed by anyone without the signing key.",
  "Which agent identity produced each record, and in what order.",
  "Which coding-agent events were captured, with events the hooks missed shown as gaps (Pro).",
];
const DOES_NOT = [
  "Records are signed by your Attestix instance; whoever holds that key could rewrite them today. Independent witnessing in Attestix Cloud is planned to close this.",
  "It is not a compliance certification. It is evidence for an assessment, not the assessment.",
  "Live revocation checks still need the issuer.",
];

function CellMark({ v }: { v: Cell }) {
  if (v === true)
    return (
      <>
        <Check aria-hidden className="mx-auto h-4 w-4 text-atx-ok" />
        <span className="sr-only">Included</span>
      </>
    );
  if (v === false)
    return (
      <>
        <X aria-hidden className="mx-auto h-4 w-4 text-atx-ink-dim" />
        <span className="sr-only">Not included</span>
      </>
    );
  return <span className="text-[13px] text-atx-ink-mid">{v}</span>;
}

export default function PlatformPage() {
  return (
    <>
      <section className="px-6 pb-20 pt-16 text-center md:pt-20">
        <div className="mx-auto max-w-[860px]">
          <p className={EYEBROW}>Platform</p>
          <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
            One <span className="text-atx-accent">evidence layer</span> for every AI agent
          </h1>
          <p className={`mx-auto mt-5 max-w-[660px] [text-wrap:balance] ${LEAD}`}>
            Framework agents, MCP clients, coding agents, and the agents you build
            yourself all write to the same signed, hash-chained record, which anyone
            can verify offline with open-source tools.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link href="/docs/getting-started" className={PILL_PRIMARY}>
              Get started <ArrowRight className="h-4 w-4" />
            </Link>
            <a href="#editions" className={PILL_GHOST}>
              Compare editions
            </a>
          </div>
        </div>
      </section>

      <section id="workflow" className="scroll-mt-20 bg-atx-bg-elev py-20">
        <div className={WRAP}>
          <div className="text-center">
            <p className={EYEBROW}>How it works</p>
            <h2 className={`mt-3 ${H2}`}>Capture, sign and chain, verify anywhere</h2>
          </div>
          <ol className="mt-12 grid gap-5 md:grid-cols-3">
            {STEPS.map((s, i) => (
              <li key={s.title} className={`rounded-2xl border p-6 ${TINT[s.tint].card}`}>
                <div className="flex items-center gap-3">
                  <span className={`grid h-10 w-10 place-items-center rounded-xl ${TINT[s.tint].chip}`}>{s.icon}</span>
                  <h3 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
                    <span className="text-atx-ink-dim">{i + 1}.</span> {s.title}
                  </h3>
                </div>
                <p className="mt-4 text-[15px] leading-[1.6] text-atx-ink-mid">{s.body}</p>
              </li>
            ))}
          </ol>
          <div className="mx-auto mt-6 flex max-w-[860px] items-start gap-3 rounded-2xl border border-dashed border-atx-line px-6 py-5">
            <FileSignature aria-hidden className="mt-0.5 h-5 w-5 shrink-0 text-atx-ink-dim" />
            <p className="text-[14px] leading-[1.6] text-atx-ink-mid">
              <span className="font-medium text-atx-ink">Attestix Cloud (in development)</span> adds a
              step between signing and verifying: checkpoints of the chain are witnessed
              independently with RFC 3161 timestamps and a public transparency log, so the
              record no longer rests on one operator&rsquo;s key alone.
            </p>
          </div>
        </div>
      </section>

      <section id="runs-on" className="scroll-mt-20 bg-atx-bg py-20">
        <div className={WRAP}>
          <div className="text-center">
            <p className={EYEBROW}>Where Attestix runs</p>
            <h2 className={`mt-3 ${H2}`}>Wherever your agents already are</h2>
          </div>
          <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
            {RUNS_ON.map((r) => (
              <div key={r.title} className="flex flex-col rounded-2xl border border-atx-line bg-atx-panel/60 p-6">
                <h3 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">{r.title}</h3>
                <p className="mt-3 flex-1 text-[14px] leading-[1.6] text-atx-ink-mid">{r.body}</p>
                <Link
                  href={r.href}
                  className="mt-5 inline-flex items-center gap-1.5 text-[14px] font-medium text-atx-ink-mid underline decoration-atx-line underline-offset-4 hover:text-atx-ink"
                >
                  {r.link} <ArrowRight aria-hidden className="h-3.5 w-3.5" />
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      <ModulesSection />

      <section id="editions" className="scroll-mt-20 bg-atx-bg py-20">
        <div className={WRAP}>
          <div className="text-center">
            <p className={EYEBROW}>Editions</p>
            <h2 className={`mt-3 ${H2}`}>Open source, Pro, and Cloud</h2>
            <p className={`mx-auto mt-4 max-w-[720px] ${LEAD}`}>
              The open-source core is the evidence format and the tools. Pro adds capture
              for coding agents. Cloud will host and witness the record for you.
            </p>
          </div>
          <div className="relative mt-12 overflow-x-auto rounded-2xl border border-atx-line">
            <table className="w-full min-w-[640px] border-collapse text-left text-[14px]">
              <caption className="sr-only">What each Attestix edition includes</caption>
              <thead>
                <tr className="bg-atx-panel/60">
                  <th scope="col" className="px-5 py-4 font-medium text-atx-ink-mid">
                    Feature
                  </th>
                  {EDITIONS.map((e) => (
                    <th key={e} scope="col" className="px-5 py-4 text-center font-semibold text-atx-ink">
                      {e}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {COMPARE.map((r) => (
                  <tr key={r.row} className="border-t border-atx-line-soft">
                    <th scope="row" className="px-5 py-3.5 font-normal text-atx-ink-mid">
                      {r.row}
                    </th>
                    {r.cells.map((c, i) => (
                      <td key={EDITIONS[i]} className="px-5 py-3.5 text-center">
                        <CellMark v={c} />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section id="coding-agents" className="scroll-mt-20 bg-atx-bg-elev py-20">
        <div className={`${WRAP} grid items-start gap-10 lg:grid-cols-2`}>
          <div>
            <p className={EYEBROW}>Coding-agent capture (Attestix Pro, early access)</p>
            <h2 className={`mt-3 ${H2}`}>A verifiable record of every coding-agent session</h2>
            <p className={`mt-5 ${LEAD}`}>
              Pro captures Claude Code today, across all of its hook events. It cross-checks
              them against local OpenTelemetry and the session transcript, so any event the
              hooks missed shows up as a gap instead of silently disappearing.
            </p>
            <ul className="mt-6 space-y-2.5 text-[15px] leading-[1.6] text-atx-ink-mid">
              <li>Per-session launcher; no permanent configuration changes.</li>
              <li>Optional policy enforcement that blocks a tool and records the denial.</li>
              <li>Verified in live runs: editing one record and cutting the end of the log were both detected.</li>
              <li>Cursor, Codex CLI, GitHub Copilot, Gemini, and other coding agents are on the roadmap.</li>
            </ul>
          </div>
          <div>
            <div className="rounded-2xl border border-atx-line bg-atx-bg-sunken p-6 font-mono-atx text-[13px] leading-[1.9]">
              <div className="text-atx-ink-faint"># record one Claude Code session</div>
              <div>
                <span className="text-atx-accent">$</span> <span className="text-atx-ink">attestix-pro run</span>{" "}
                <span className="text-atx-info">--</span> claude
              </div>
              <div className="text-atx-ink-faint"># check the chain afterwards</div>
              <div>
                <span className="text-atx-accent">$</span> <span className="text-atx-ink">attestix-pro verify</span>
              </div>
            </div>
            <h3 className="mt-8 text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">What it detects</h3>
            <dl className="mt-4 grid gap-3 sm:grid-cols-2">
              {DETECTS.map(([k, v]) => (
                <div key={k} className="rounded-xl border border-atx-line bg-atx-panel/60 px-4 py-3.5">
                  <dt className="text-[15px] font-medium text-atx-ink">{k}</dt>
                  <dd className="mt-1 text-[13.5px] leading-[1.55] text-atx-ink-mid">{v}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </section>

      <section id="limits" className="scroll-mt-20 bg-atx-bg py-20">
        <div className={WRAP}>
          <div className="text-center">
            <p className={EYEBROW}>Honest limits</p>
            <h2 className={`mt-3 ${H2}`}>What the evidence proves, and what it does not</h2>
          </div>
          <div className="mx-auto mt-12 grid max-w-[1040px] gap-5 md:grid-cols-2">
            <div className={`rounded-2xl border p-6 ${TINT.ok.card}`}>
              <h3 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">It proves</h3>
              <ul className="mt-4 space-y-3 text-[15px] leading-[1.6] text-atx-ink-mid">
                {PROVES.map((p) => (
                  <li key={p} className="flex gap-2.5">
                    <Check aria-hidden className="mt-1 h-4 w-4 shrink-0 text-atx-ok" />
                    {p}
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-2xl border border-atx-line bg-atx-panel/60 p-6">
              <h3 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">It does not</h3>
              <ul className="mt-4 space-y-3 text-[15px] leading-[1.6] text-atx-ink-mid">
                {DOES_NOT.map((p) => (
                  <li key={p} className="flex gap-2.5">
                    <X aria-hidden className="mt-1 h-4 w-4 shrink-0 text-atx-ink-dim" />
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-atx-bg-elev py-20">
        <div className={`${WRAP} text-center`}>
          <h2 className={H2}>Start with the open-source core</h2>
          <p className={`mx-auto mt-4 max-w-[640px] ${LEAD}`}>
            Install it in a minute, or talk to us about coding-agent capture and hosted
            evidence.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link href="/docs/getting-started" className={PILL_PRIMARY}>
              Get started <ArrowRight className="h-4 w-4" />
            </Link>
            <a href="https://cal.com/vibetensor/attestix" target="_blank" rel="noopener noreferrer" className={PILL_GHOST}>
              Talk to us <span aria-hidden>&#8599;</span>
            </a>
            <a
              href="mailto:info@vibetensor.com?subject=Attestix%20Pro%20and%20Cloud%20early%20access"
              className={PILL_GHOST}
            >
              Join the Pro and Cloud early access list
            </a>
          </div>
        </div>
      </section>
    </>
  );
}
