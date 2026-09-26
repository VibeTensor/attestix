const WRAP = "mx-auto w-full max-w-[1200px] px-6";
const H2 = "text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink [text-wrap:balance]";
const LEAD = "text-[17.5px] leading-[1.6] text-atx-ink-mid";

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
    "No record of which Article 43 conformity route a system took",
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
    "Article 43 routes recorded; self-assessment refused where a notified body is required",
    "No cloud dependency, works offline, JSON-file storage",
  ],
};

const TONE = {
  bad: { card: "border-atx-err/30 bg-atx-err/[0.05]", tag: "text-atx-err", dot: "bg-atx-err" },
  good: { card: "border-atx-accent/30 bg-atx-accent/[0.05]", tag: "text-atx-accent", dot: "bg-atx-accent" },
} as const;

function Col({ col }: { col: Column }) {
  const t = TONE[col.tone];
  return (
    <div className={`rounded-2xl border p-7 text-left ${t.card}`}>
      <p className={`text-[14px] font-medium ${t.tag}`}>{col.tag}</p>
      <h3 className="mt-3 text-[21px] font-semibold leading-[1.25] tracking-[-0.48px] text-atx-ink">
        {col.title}
      </h3>
      <p className="mt-3 text-[15px] leading-[1.6] text-atx-ink-mid">{col.lead}</p>
      <ul className="mt-6 space-y-2.5">
        {col.bullets.map((b) => (
          <li key={b} className="flex gap-3 text-[14px] leading-[1.55] text-atx-ink-mid">
            <span className={`mt-2 block h-1.5 w-1.5 shrink-0 rounded-full ${t.dot}`} />
            {b}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function ProblemSection() {
  return (
    <section id="problem" className="scroll-mt-20 bg-atx-bg py-20">
      <div className={WRAP}>
        <div className="text-center">
          <h2 className={H2}>
            Every AI agent will need an audit trail.
            <br />
            None of the existing tools produce one.
          </h2>
          <p className={`mx-auto mt-4 max-w-[760px] ${LEAD}`}>
            Existing compliance platforms produce organisational dashboards,
            not machine-readable, cryptographically verifiable evidence that a
            specific agent can present to a regulator, an auditor, or another
            agent. Agent identity is fragmenting across walled gardens.
            Attestix fills the gap.
          </p>
        </div>

        <div className="mx-auto mt-12 grid max-w-[1040px] gap-5 md:grid-cols-2">
          <Col col={BEFORE} />
          <Col col={AFTER} />
        </div>
      </div>
    </section>
  );
}
