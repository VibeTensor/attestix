import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";
import Link from "next/link";

export const metadata = constructMetadata({
  title: "Research",
  description:
    "The research paper behind Attestix. IEEE-format LaTeX, open-access, peer review in progress.",
});

export default function ResearchPage() {
  return (
    <section className="mx-auto max-w-[1080px] px-7 py-24">
      <AtxEyebrow>Research</AtxEyebrow>
      <h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
        Attestation
        <br />
        infrastructure
        <br />
        <em className="italic text-atx-accent">for AI agents.</em>
      </h1>

      <div className="mt-10 flex flex-wrap items-center gap-4 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        <span>IEEE format</span>
        <span>&middot;</span>
        <span>Open access (Apache 2.0)</span>
        <span>&middot;</span>
        <span>Peer review in progress</span>
      </div>

      <div className="mt-10 space-y-6 text-[15px] leading-[1.7] text-atx-ink-mid">
        <p>
          The paper introduces a machine-verifiable trust layer for autonomous
          AI agents. Three primitives are combined: Unified Agent Identity
          Tokens (UAIT) bridging MCP OAuth, A2A, DIDs, and API keys; W3C
          Verifiable Credentials with Ed25519Signature2020 proofs; and a
          hash-chained audit trail with optional Base L2 testnet anchoring via
          the Ethereum Attestation Service.
        </p>
        <p>
          The system is evaluated against five open standards (RFC 8032, W3C
          Verifiable Credentials 1.1, W3C DID 1.0, UCAN v0.9, MCP 1.8) through
          91 automated conformance benchmarks, and against ten EU AI Act
          articles plus Annex III and Annex V through compliance-workflow tests.
          Ed25519 sign + verify runs at 0.22 ms median. End-to-end credential
          issuance runs at 21 ms median on commodity hardware.
        </p>
        <p>
          The artefact and all tests are open-source under Apache 2.0 and
          published on PyPI as the <code className="rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-1.5 py-0.5 font-mono-atx text-[13px] text-atx-accent">attestix</code> package, alongside an MCP server registered on the
          Model Context Protocol registry.
        </p>
      </div>

      <h2 className="mt-16 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        Contributions
      </h2>
      <ul className="mt-4 space-y-2 text-[14px] leading-[1.7] text-atx-ink-mid">
        <li>
          <strong className="text-atx-ink">1.</strong> A protocol-agnostic
          identity token (UAIT) that unifies MCP, A2A, DIDs, OAuth, API keys.
        </li>
        <li>
          <strong className="text-atx-ink">2.</strong> An automated EU AI Act
          compliance pipeline from risk classification to Annex V declaration
          as a W3C Verifiable Credential.
        </li>
        <li>
          <strong className="text-atx-ink">3.</strong> A hash-chained,
          tamper-evident audit trail verifiable offline.
        </li>
        <li>
          <strong className="text-atx-ink">4.</strong> Optional on-chain
          anchoring via EAS on Base L2 testnet with Merkle batching.
        </li>
        <li>
          <strong className="text-atx-ink">5.</strong> An MCP-native,
          open-source reference implementation validated by 585 automated
          tests (494 functional + 91 RFC / W3C conformance benchmarks).
        </li>
      </ul>

      <h2 className="mt-16 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        Read the full paper
      </h2>
      <div className="mt-4 flex flex-wrap gap-3">
        <Link
          href="/docs/project/research"
          className="inline-flex h-10 items-center rounded-atx-md bg-atx-accent px-5 text-[13px] font-medium text-[oklch(0.14_0.01_180)] transition-colors hover:bg-atx-accent-deep"
        >
          Read in docs
        </Link>
        <a
          href="https://github.com/VibeTensor/attestix/tree/main/paper"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex h-10 items-center rounded-atx-md border border-atx-line px-5 text-[13px] font-medium text-atx-ink transition-colors hover:border-atx-ink-dim hover:bg-atx-panel"
        >
          LaTeX source on GitHub
        </a>
      </div>
    </section>
  );
}
