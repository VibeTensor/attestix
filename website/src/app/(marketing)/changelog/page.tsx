import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";
import Link from "next/link";

export const metadata = constructMetadata({
  title: "Changelog",
  description: "Attestix release history.",
});

interface Release {
  version: string;
  date: string;
  headline: string;
  items: string[];
}

const RELEASES: Release[] = [
  {
    version: "0.4.1",
    date: "2026-06-24",
    headline: "Post-quantum hybrid signing, verification hardening, fail-closed API auth",
    items: [
      "Post-quantum / hybrid signing (ML-DSA-65 + Ed25519, optional [pqc] extra)",
      "Credential verification key-binding hardening (decode key from the trust anchor)",
      "Fail-closed REST API auth when ATTESTIX_API_KEY is unset",
      "Cloud-to-OSS audit-chain re-verification fix (preserve the chain tenant on import)",
      "585 passing tests (494 functional + 91 conformance)",
    ],
  },
  {
    version: "0.4.0",
    date: "2026-05-30",
    headline: "First stable 0.4.0: embeddable, multi-tenant, portable foundation",
    items: [
      "First stable 0.4.0: embeddable, multi-tenant, portable foundation",
      "Pluggable storage + signer protocols (Postgres / HSM-KMS without forking)",
      "Portability bundle export/import (cloud-to-OSS)",
      "Promoted from a clean 10/10 source-blind RC validation",
    ],
  },
  {
    version: "0.3.0",
    date: "2026-04-17",
    headline: "Real framework integrations, CI/CD, delegation chain auth fix",
    items: [
      "Real LangChain integration via BaseCallbackHandler",
      "Real OpenAI Agents SDK integration via MCPServerStdio",
      "Real CrewAI integration via MCPServerAdapter",
      "Critical delegation chain auth bypass fix (parent token verification, capability attenuation)",
      "Article 43 Annex III differentiation for conformity assessment",
      "7 framework integration examples, 15 integration tests",
      "Security batch: SSRF, API timing, exception leaks, display_name sanitisation, key file permissions",
      "GitHub Actions CI/CD (pytest matrix on Python 3.10-3.13, lint, security, publish)",
      "4 HIGH severity security fixes, PyJWT CVE mitigation, dependency pinning",
      "358 tests total (194 unit + 45 e2e + 15 integration + 14 tool + 91 conformance benchmarks + 11 security)",
    ],
  },
  {
    version: "0.2.5",
    date: "2026-03-15",
    headline: "EAS schema correctness, hardened Attested event decoding",
    items: [
      "EAS schema UID correctness for Base L2 testnet",
      "Hardened Attested event decoding",
      "Additional conformance benchmarks across W3C VC, DID, UCAN",
    ],
  },
  {
    version: "0.2.0",
    date: "2026-02-20",
    headline: "Blockchain anchoring + conformance benchmarks",
    items: [
      "Blockchain anchoring to Base L2 testnet via Ethereum Attestation Service",
      "Merkle batch anchoring for cost efficiency",
      "91 conformance benchmark tests validating RFC 8032, W3C VC, W3C DID, UCAN, MCP",
      "284 tests total at release (193 functional + 91 conformance)",
    ],
  },
  {
    version: "0.1.0",
    date: "2026-01-20",
    headline: "First public release",
    items: [
      "47 MCP tools across 9 modules",
      "44 REST endpoints",
      "W3C Verifiable Credentials 1.1 with Ed25519Signature2020",
      "W3C DID 1.0 (did:key, did:web)",
      "UCAN v0.9 delegation",
      "EU AI Act automation: Articles 5, 9-15, 43, 72, 73 plus Annex III and Annex V",
      "GDPR Article 17 (right to erasure)",
      "MCP 1.8+ protocol compliance",
      "Apache 2.0 license",
    ],
  },
];

export default function ChangelogPage() {
  return (
    <>
      <section className="bg-atx-bg px-6 pb-16 pt-16 text-center md:pt-20">
        <div className="mx-auto max-w-[860px]">
          <AtxEyebrow>Changelog</AtxEyebrow>
          <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
            Release <span className="text-atx-accent">history.</span>
          </h1>
          <p className="mx-auto mt-5 max-w-[640px] text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
            Attestix is in active development. Every release is tagged on GitHub,
            published to PyPI, and accompanied by a full changelog. For detailed
            technical notes see the repository{" "}
            <Link
              href="https://github.com/VibeTensor/attestix/releases"
              target="_blank"
              rel="noopener noreferrer"
              className="text-atx-ink underline decoration-atx-line underline-offset-4 transition-colors duration-200 hover:decoration-atx-ink-dim"
            >
              releases page
            </Link>
            .
          </p>
        </div>
      </section>

      <section className="bg-atx-bg-elev py-20">
        <ol className="mx-auto w-full max-w-[1000px] space-y-5 px-6">
          {RELEASES.map((r) => (
            <li
              key={r.version}
              className="relative grid gap-6 rounded-2xl border border-atx-line bg-atx-panel/60 p-6 transition-colors duration-200 hover:border-atx-ink-dim md:grid-cols-[180px_1fr] md:p-7"
            >
              <div>
                <div className="text-[32px] font-normal leading-none tracking-[-0.03em] text-atx-accent">
                  v{r.version}
                </div>
                <div className="mt-2 text-[13px] text-atx-ink-dim">
                  <time dateTime={r.date}>{r.date}</time>
                </div>
              </div>
              <div>
                <h2 className="text-[19px] font-semibold leading-[1.3] tracking-[-0.48px] text-atx-ink">
                  {r.headline}
                </h2>
                <ul className="mt-4 space-y-2">
                  {r.items.map((it) => (
                    <li
                      key={it}
                      className="flex gap-3 text-[15px] leading-[1.6] text-atx-ink-mid"
                    >
                      <span className="mt-2.5 block h-1 w-1 shrink-0 rounded-full bg-atx-accent" />
                      {it}
                    </li>
                  ))}
                </ul>
              </div>
            </li>
          ))}
        </ol>
      </section>
    </>
  );
}
