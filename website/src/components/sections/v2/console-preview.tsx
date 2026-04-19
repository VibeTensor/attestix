import Link from "next/link";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";

function PreviewCard() {
  return (
    <div className="overflow-hidden rounded-atx-md border border-atx-line-soft bg-atx-panel shadow-[var(--atx-shadow-md)]">
      <div className="flex items-center gap-3 border-b border-atx-line-soft px-4 py-2.5 font-mono-atx text-[11px] text-atx-ink-dim">
        <span className="flex gap-1.5">
          <span className="inline-block h-2 w-2 rounded-full bg-atx-err/60" />
          <span className="inline-block h-2 w-2 rounded-full bg-atx-warn/60" />
          <span className="inline-block h-2 w-2 rounded-full bg-atx-ok/60" />
        </span>
        <span>Attestix Console / localhost:8501</span>
        <span className="ml-auto flex items-center gap-2 text-atx-ok">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-atx-ok" />
          connected
        </span>
      </div>

      <div className="grid grid-cols-[180px_1fr]">
        <nav className="border-r border-atx-line-soft bg-atx-bg-sunken p-3">
          <div className="mb-2 font-mono-atx text-[9.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
            Operate
          </div>
          {[
            { l: "Agents", n: 8, active: true },
            { l: "Compliance", n: 6 },
            { l: "Credentials", n: 2 },
            { l: "Audit trail", n: 10 },
            { l: "Anchors", n: 7 },
          ].map((s) => (
            <div
              key={s.l}
              className={`flex items-center justify-between rounded-atx-xs px-2 py-1.5 font-mono-atx text-[11px] ${
                s.active
                  ? "bg-atx-panel-hi text-atx-accent"
                  : "text-atx-ink-dim"
              }`}
            >
              <span>{s.l}</span>
              <span className="text-[10px] text-atx-ink-faint">{s.n}</span>
            </div>
          ))}
        </nav>

        <div className="p-5">
          <div className="flex items-center justify-between">
            <div className="font-serif text-[22px] leading-none text-atx-ink">
              Agents
            </div>
            <div className="font-mono-atx text-[11px] text-atx-ink-dim">
              8 / 8 agents
            </div>
          </div>

          <table className="mt-4 w-full text-left font-mono-atx text-[11px]">
            <thead>
              <tr className="text-atx-ink-faint">
                <th className="pb-2 font-medium">Agent</th>
                <th className="pb-2 font-medium">Risk</th>
                <th className="pb-2 font-medium">Status</th>
                <th className="pb-2 text-right font-medium">Trust</th>
              </tr>
            </thead>
            <tbody>
              {[
                { n: "quarterly-analyst-v2", r: "HIGH", s: "compl", t: 94 },
                { n: "clinical-triage-bot", r: "HIGH", s: "gap", t: 78 },
                { n: "supply-chain-optimizer", r: "LIM", s: "compl", t: 89 },
                { n: "fraud-detector", r: "PRO", s: "compl", t: 96 },
                { n: "doc-summarizer", r: "MIN", s: "compl", t: 91 },
              ].map((a) => (
                <tr
                  key={a.n}
                  className="border-t border-atx-line-soft/60 text-atx-ink"
                >
                  <td className="py-2">{a.n}</td>
                  <td className="py-2 text-atx-accent">{a.r}</td>
                  <td className="py-2">
                    <span
                      className={`inline-block h-1.5 w-1.5 rounded-full ${
                        a.s === "compl"
                          ? "bg-atx-ok"
                          : a.s === "gap"
                            ? "bg-atx-warn"
                            : "bg-atx-err"
                      }`}
                    />
                  </td>
                  <td className="py-2 text-right">
                    <div className="inline-flex items-center gap-2">
                      <span className="block h-0.5 w-10 rounded-full bg-atx-line-soft">
                        <span
                          className="block h-0.5 rounded-full bg-atx-accent"
                          style={{ width: `${a.t}%` }}
                        />
                      </span>
                      <span className="text-atx-ink-dim">
                        {(a.t / 100).toFixed(2)}
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function ArchitectureDiagram() {
  return (
    <svg
      viewBox="0 0 720 560"
      role="img"
      aria-label="Attestix architecture flow with delegation and discovery axes"
      className="w-full"
    >
      <defs>
        <marker
          id="atx-arrow"
          viewBox="0 0 10 10"
          refX="9"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path d="M0,0 L10,5 L0,10 z" fill="var(--atx-accent)" />
        </marker>
        <marker
          id="atx-arrow-dim"
          viewBox="0 0 10 10"
          refX="9"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path d="M0,0 L10,5 L0,10 z" fill="var(--atx-ink-dim)" />
        </marker>
      </defs>

      {/* Discovery column (right of the main flow) */}
      <g
        fontFamily="var(--font-mono-atx)"
        fontSize="9.5"
        textAnchor="middle"
        fill="var(--atx-ink)"
      >
        <text
          x="640"
          y="18"
          fill="var(--atx-ink-faint)"
          fontSize="9"
          textAnchor="end"
        >
          DISCOVERY AXIS
        </text>
        <rect
          x="550"
          y="30"
          width="160"
          height="48"
          rx="4"
          fill="var(--atx-bg-sunken)"
          stroke="var(--atx-line-soft)"
          strokeDasharray="2 2"
        />
        <text x="630" y="50" fill="var(--atx-ink-dim)" fontSize="9">
          /.well-known/
        </text>
        <text x="630" y="65" fill="var(--atx-ink)">
          agent.json
        </text>
        <path
          d="M 360 34 L 550 50"
          stroke="var(--atx-ink-dim)"
          strokeWidth="1"
          fill="none"
          strokeDasharray="3 3"
          markerEnd="url(#atx-arrow-dim)"
        />
      </g>

      {/* Delegation column (left of the main flow) */}
      <g
        fontFamily="var(--font-mono-atx)"
        fontSize="9.5"
        textAnchor="middle"
        fill="var(--atx-ink)"
      >
        <text
          x="20"
          y="18"
          fill="var(--atx-ink-faint)"
          fontSize="9"
          textAnchor="start"
        >
          DELEGATION AXIS
        </text>
        <rect
          x="10"
          y="30"
          width="140"
          height="48"
          rx="4"
          fill="var(--atx-accent-soft)"
          stroke="var(--atx-accent)"
          strokeOpacity="0.6"
        />
        <text x="80" y="50" fill="var(--atx-accent)" fontSize="9">
          UCAN v0.9
        </text>
        <text x="80" y="65" fill="var(--atx-ink)">
          delegated sub-agent
        </text>
        <path
          d="M 200 34 L 150 50"
          stroke="var(--atx-accent)"
          strokeWidth="1"
          fill="none"
          strokeDasharray="3 3"
          markerEnd="url(#atx-arrow)"
        />
      </g>

      <g
        fontFamily="var(--font-mono-atx)"
        fontSize="10.5"
        textAnchor="middle"
        fill="var(--atx-ink)"
      >
        {/* Agent (wider to contain framework list) */}
        <g>
          <rect
            x="170"
            y="10"
            width="220"
            height="48"
            rx="4"
            fill="var(--atx-panel)"
            stroke="var(--atx-line)"
          />
          <text x="280" y="32" fill="var(--atx-ink-dim)" fontSize="9">
            AGENT
          </text>
          <text x="280" y="48" fill="var(--atx-ink)">
            LangChain / OpenAI / CrewAI
          </text>
        </g>
        <path
          d="M 280 58 L 280 80"
          stroke="var(--atx-accent)"
          strokeWidth="1.2"
          fill="none"
          markerEnd="url(#atx-arrow)"
        />

        {/* Transports */}
        <g>
          <rect
            x="120"
            y="80"
            width="110"
            height="34"
            rx="4"
            fill="var(--atx-bg-sunken)"
            stroke="var(--atx-line-soft)"
          />
          <text x="175" y="101" fill="var(--atx-ink-dim)">
            MCP server
          </text>

          <rect
            x="240"
            y="80"
            width="80"
            height="34"
            rx="4"
            fill="var(--atx-bg-sunken)"
            stroke="var(--atx-line-soft)"
          />
          <text x="280" y="101" fill="var(--atx-ink-dim)">
            REST API
          </text>

          <rect
            x="330"
            y="80"
            width="110"
            height="34"
            rx="4"
            fill="var(--atx-bg-sunken)"
            stroke="var(--atx-line-soft)"
          />
          <text x="385" y="101" fill="var(--atx-ink-dim)">
            Python library
          </text>
        </g>
        <path
          d="M 280 114 L 280 136"
          stroke="var(--atx-accent)"
          strokeWidth="1.2"
          fill="none"
          markerEnd="url(#atx-arrow)"
        />

        {/* Nine modules */}
        <g>
          <rect
            x="40"
            y="136"
            width="480"
            height="90"
            rx="4"
            fill="var(--atx-panel)"
            stroke="var(--atx-accent)"
            strokeOpacity="0.5"
          />
          <text
            x="60"
            y="156"
            fill="var(--atx-accent)"
            fontSize="9"
            textAnchor="start"
          >
            9 MODULES / 47 MCP TOOLS
          </text>
          {[
            "Identity",
            "Agent Cards",
            "DID",
            "Delegation",
            "Reputation",
            "Compliance",
            "Credentials",
            "Provenance",
            "Blockchain",
          ].map((m, i) => {
            const col = i % 5;
            const row = Math.floor(i / 5);
            const x = 60 + col * 90;
            const y = 174 + row * 26;
            return (
              <g key={m}>
                <rect
                  x={x}
                  y={y}
                  width="80"
                  height="20"
                  rx="2"
                  fill="var(--atx-bg-sunken)"
                  stroke="var(--atx-line-soft)"
                />
                <text x={x + 40} y={y + 14} fill="var(--atx-ink-mid)">
                  {m}
                </text>
              </g>
            );
          })}
        </g>
        <path
          d="M 280 226 L 280 244"
          stroke="var(--atx-accent)"
          strokeWidth="1.2"
          fill="none"
          markerEnd="url(#atx-arrow)"
        />

        {/* Cryptographic output container wrapping the 4 output primitives */}
        <g>
          <rect
            x="120"
            y="244"
            width="320"
            height="140"
            rx="6"
            fill="var(--atx-panel)"
            stroke="var(--atx-accent)"
            strokeOpacity="0.5"
          />
          <text
            x="140"
            y="262"
            fill="var(--atx-accent)"
            fontSize="9"
            textAnchor="start"
          >
            CRYPTOGRAPHIC OUTPUT
          </text>

          {/* Ed25519 sign */}
          <rect
            x="140"
            y="272"
            width="130"
            height="44"
            rx="4"
            fill="var(--atx-bg-sunken)"
            stroke="var(--atx-line-soft)"
          />
          <text x="205" y="290" fill="var(--atx-ink-dim)" fontSize="9">
            Ed25519 SIGN
          </text>
          <text x="205" y="305" fill="var(--atx-ink)">
            RFC 8032
          </text>

          {/* Hash chain */}
          <rect
            x="290"
            y="272"
            width="130"
            height="44"
            rx="4"
            fill="var(--atx-bg-sunken)"
            stroke="var(--atx-line-soft)"
          />
          <text x="355" y="290" fill="var(--atx-ink-dim)" fontSize="9">
            HASH CHAIN
          </text>
          <text x="355" y="305" fill="var(--atx-ink)">
            SHA-256 Merkle
          </text>

          {/* Verifiable credential */}
          <rect
            x="140"
            y="326"
            width="130"
            height="44"
            rx="4"
            fill="var(--atx-accent-soft)"
            stroke="var(--atx-accent)"
          />
          <text x="205" y="344" fill="var(--atx-accent)" fontSize="9">
            VERIFIABLE CREDENTIAL
          </text>
          <text x="205" y="359" fill="var(--atx-ink)">
            W3C VC 1.1
          </text>

          {/* Base L2 anchor */}
          <rect
            x="290"
            y="326"
            width="130"
            height="44"
            rx="4"
            fill="var(--atx-bg-sunken)"
            stroke="var(--atx-line-soft)"
            strokeDasharray="3 3"
          />
          <text x="355" y="344" fill="var(--atx-ink-dim)" fontSize="9">
            BASE L2 (optional)
          </text>
          <text x="355" y="359" fill="var(--atx-ink-mid)">
            EAS testnet anchor
          </text>

          {/* Internal flow arrows inside the container */}
          <path
            d="M 205 316 L 205 326"
            stroke="var(--atx-accent)"
            strokeWidth="1"
            fill="none"
            markerEnd="url(#atx-arrow)"
          />
          <path
            d="M 355 316 L 355 326"
            stroke="var(--atx-ink-dim)"
            strokeWidth="1"
            fill="none"
            markerEnd="url(#atx-arrow-dim)"
            strokeDasharray="3 3"
          />
        </g>

        {/* Container -> verifiers */}
        <path
          d="M 280 384 L 280 394"
          stroke="var(--atx-accent)"
          strokeWidth="1.2"
          fill="none"
          markerEnd="url(#atx-arrow)"
        />

        {/* Verifier ring */}
        <g>
          <rect
            x="40"
            y="394"
            width="480"
            height="100"
            rx="4"
            fill="var(--atx-bg-sunken)"
            stroke="var(--atx-line-soft)"
          />
          <text
            x="60"
            y="414"
            fill="var(--atx-ink-dim)"
            fontSize="9"
            textAnchor="start"
          >
            VERIFIERS
          </text>
          <g fontSize="10">
            <rect
              x="60"
              y="432"
              width="140"
              height="44"
              rx="3"
              fill="var(--atx-panel)"
              stroke="var(--atx-line)"
            />
            <text x="130" y="452" fill="var(--atx-ink-mid)" fontSize="9">
              REGULATOR
            </text>
            <text x="130" y="468" fill="var(--atx-ink)">
              did:web:eu.regulator
            </text>

            <rect
              x="210"
              y="432"
              width="140"
              height="44"
              rx="3"
              fill="var(--atx-panel)"
              stroke="var(--atx-line)"
            />
            <text x="280" y="452" fill="var(--atx-ink-mid)" fontSize="9">
              AUDITOR
            </text>
            <text x="280" y="468" fill="var(--atx-ink)">
              offline verify
            </text>

            <rect
              x="360"
              y="432"
              width="140"
              height="44"
              rx="3"
              fill="var(--atx-panel)"
              stroke="var(--atx-line)"
            />
            <text x="430" y="452" fill="var(--atx-ink-mid)" fontSize="9">
              OTHER AGENT
            </text>
            <text x="430" y="468" fill="var(--atx-ink)">
              A2A / MCP
            </text>
          </g>
        </g>
      </g>
    </svg>
  );
}

export function ConsolePreviewSection() {
  return (
    <section
      id="console-preview"
      className="border-t border-atx-line-soft py-24"
    >
      <div className="mx-auto max-w-[1320px] px-7">
        <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
          <div>
            <AtxEyebrow number="04">The product</AtxEyebrow>
            <h2 className="mt-3 font-serif text-[clamp(28px,3.2vw,40px)] leading-[1.15] tracking-[-0.01em] text-atx-ink">
              A console that
              <br />
              behaves like
              <br />
              <em className="italic text-atx-accent">compliance.</em>
            </h2>
          </div>
          <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
            Every agent, every credential, every hash. The Attestix console is
            a working surface across the full stack with the same primitives
            the CLI, MCP server, and REST API expose. The diagram shows how
            the pieces fit together under the hood.
          </p>
        </div>

        <div className="mt-14 grid gap-8 lg:grid-cols-[1.15fr_1fr]">
          <div className="flex flex-col gap-5">
            <PreviewCard />
            <div className="flex flex-wrap items-center gap-3">
              <Link
                href="/console"
                className="group inline-flex h-10 items-center gap-2 rounded-atx-md bg-atx-accent px-5 text-[13px] font-medium text-[oklch(0.14_0.01_180)] transition-colors hover:bg-atx-accent-deep"
              >
                Launch interactive console
                <span className="font-mono-atx transition-transform group-hover:translate-x-0.5">
                  &rarr;
                </span>
              </Link>
              <span className="font-mono-atx text-[11px] uppercase tracking-[0.1em] text-atx-ink-faint">
                data is simulated
              </span>
            </div>
          </div>

          <div className="rounded-atx-md border border-atx-line-soft bg-atx-panel p-6">
            <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
              Architecture
            </div>
            <h3 className="mt-1 font-serif text-[22px] leading-tight text-atx-ink">
              From agent to regulator
            </h3>
            <div className="mt-4">
              <ArchitectureDiagram />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
