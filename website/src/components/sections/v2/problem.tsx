import { AtxEyebrow } from "@/components/atx/atx-eyebrow";

interface Column {
  tag: string;
  title: string;
  lead: string;
  bullets: string[];
  tone: "bad" | "good";
}

const BEFORE: Column = {
  tag: "Before Attestix",
  title: "PDFs, spreadsheets, promises.",
  lead: "Compliance artefacts that exist in slide decks and screenshots, unverifiable by any external system.",
  tone: "bad",
  bullets: [
    "Human-readable reports with no cryptographic binding",
    "Identity scattered across Entra, AgentCore, A2A, ERC-8004",
    "Audit trails stored in vendor databases, no tamper-evidence",
    "High-risk systems self-assessing (blocked under Article 43)",
    "No offline-verifiable proof for regulators",
  ],
};

const AFTER: Column = {
  tag: "With Attestix",
  title: "Signed. Anchored. Offline-verifiable.",
  lead: "Every artefact signed Ed25519, chained SHA-256, optionally anchored to Base L2 testnet via the Ethereum Attestation Service.",
  tone: "good",
  bullets: [
    "W3C Verifiable Credentials with Ed25519Signature2020",
    "Unified Agent Identity Tokens bridge MCP, A2A, DIDs, OAuth",
    "Hash-chained audit trail, tamper-evident by construction",
    "Article 43 enforcement, high-risk triggers third-party required",
    "No cloud dependency, works offline, JSON-file storage",
  ],
};

function Col({ col }: { col: Column }) {
  const border =
    col.tone === "bad"
      ? "border-atx-err/35 bg-atx-err/[0.04]"
      : "border-atx-accent/35 bg-atx-accent-soft";
  const tagColor =
    col.tone === "bad" ? "text-atx-err" : "text-atx-accent";
  return (
    <div className={`rounded-atx-md border p-8 ${border}`}>
      <div
        className={`font-mono-atx text-[11px] uppercase tracking-[0.14em] ${tagColor}`}
      >
        {col.tag}
      </div>
      <h3 className="mt-4 font-serif text-[28px] leading-tight text-atx-ink">
        {col.title}
      </h3>
      <p className="mt-3 text-[14.5px] leading-[1.6] text-atx-ink-mid">
        {col.lead}
      </p>
      <ul className="mt-6 space-y-2.5">
        {col.bullets.map((b) => (
          <li
            key={b}
            className="flex gap-3 text-[13.5px] leading-[1.55] text-atx-ink-mid"
          >
            <span
              className={
                col.tone === "bad"
                  ? "mt-2 block h-1 w-1 shrink-0 rounded-full bg-atx-err"
                  : "mt-2 block h-1 w-1 shrink-0 rounded-full bg-atx-accent"
              }
            />
            {b}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function ProblemSection() {
  return (
    <section id="problem" className="border-t border-atx-line-soft py-24">
      <div className="mx-auto max-w-[1320px] px-7">
        <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
          <div>
            <AtxEyebrow number="01">The gap</AtxEyebrow>
            <h2 className="mt-3 font-serif text-[clamp(28px,3.2vw,40px)] leading-[1.15] tracking-[-0.01em] text-atx-ink">
              Every AI agent will need an audit trail.
              <br />
              None of the existing tools produce one.
            </h2>
          </div>
          <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
            Existing compliance platforms produce organisational dashboards,
            not machine-readable, cryptographically verifiable evidence that a
            specific agent can present to a regulator, an auditor, or another
            agent. Agent identity is fragmenting across walled gardens.
            Attestix fills the gap.
          </p>
        </div>

        <div className="mt-14 grid gap-6 md:grid-cols-2">
          <Col col={BEFORE} />
          <Col col={AFTER} />
        </div>
      </div>
    </section>
  );
}
