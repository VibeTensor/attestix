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
    <section className="mx-auto max-w-[1320px] px-7 py-24">
      <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
        <div>
          <AtxEyebrow>Changelog</AtxEyebrow>
          <h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
            Release
            <br />
            <em className="italic text-atx-accent">history.</em>
          </h1>
        </div>
        <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
          Attestix is in active development. Every release is tagged on GitHub,
          published to PyPI, and accompanied by a full changelog. For detailed
          technical notes see the repository{" "}
          <Link
            href="https://github.com/VibeTensor/attestix/releases"
            target="_blank"
            rel="noopener noreferrer"
            className="text-atx-accent hover:underline"
          >
            releases page
          </Link>
          .
        </p>
      </div>

      <ol className="mt-14 space-y-10">
        {RELEASES.map((r) => (
          <li
            key={r.version}
            className="relative grid gap-6 rounded-atx-md border border-atx-line-soft bg-atx-panel p-7 md:grid-cols-[200px_1fr]"
          >
            <div>
              <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
                {r.date}
              </div>
              <div className="mt-2 font-serif text-[32px] leading-none text-atx-accent">
                v{r.version}
              </div>
            </div>
            <div>
              <h2 className="font-serif text-[22px] leading-tight text-atx-ink">
                {r.headline}
              </h2>
              <ul className="mt-4 space-y-2">
                {r.items.map((it) => (
                  <li
                    key={it}
                    className="flex gap-3 text-[13.5px] leading-[1.55] text-atx-ink-mid"
                  >
                    <span className="mt-2 block h-1 w-1 shrink-0 rounded-full bg-atx-accent" />
                    {it}
                  </li>
                ))}
              </ul>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
