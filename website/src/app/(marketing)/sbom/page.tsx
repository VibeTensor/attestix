import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "SBOM",
  description: "Attestix software bill of materials.",
});

interface Dep {
  name: string;
  version: string;
  purpose: string;
  license: string;
}

const RUNTIME: Dep[] = [
  { name: "cryptography", version: ">= 42.0", purpose: "Ed25519, PBKDF2, SHA-256", license: "Apache 2.0 / BSD" },
  { name: "pynacl", version: ">= 1.5", purpose: "Ed25519 keypair operations", license: "Apache 2.0" },
  { name: "pyjwt", version: ">= 2.8.1", purpose: "UCAN JWT signing + verify", license: "MIT" },
  { name: "jsonschema", version: ">= 4.21", purpose: "W3C VC schema validation", license: "MIT" },
  { name: "multiformats", version: ">= 0.3", purpose: "Multibase, Multicodec", license: "MIT" },
  { name: "canonicaljson", version: ">= 2.0", purpose: "RFC 8785 canonicalisation", license: "Apache 2.0" },
  { name: "httpx", version: ">= 0.26", purpose: "did:web resolution, remote verify", license: "BSD" },
  { name: "fastapi", version: ">= 0.110", purpose: "REST API surface", license: "MIT" },
  { name: "uvicorn", version: ">= 0.27", purpose: "ASGI server", license: "BSD" },
  { name: "pydantic", version: ">= 2.6", purpose: "Schema models", license: "MIT" },
  { name: "mcp", version: ">= 1.8", purpose: "MCP protocol runtime", license: "MIT" },
  { name: "eth-account", version: ">= 0.11", purpose: "Base L2 testnet signing", license: "MIT" },
  { name: "web3", version: ">= 6.15", purpose: "EAS contract calls", license: "MIT" },
];

const DEV: Dep[] = [
  { name: "pytest", version: ">= 8.0", purpose: "Test runner", license: "MIT" },
  { name: "pytest-asyncio", version: ">= 0.23", purpose: "Async tests", license: "Apache 2.0" },
  { name: "pytest-benchmark", version: ">= 4.0", purpose: "Performance benchmarks", license: "BSD" },
  { name: "ruff", version: ">= 0.3", purpose: "Lint + format", license: "MIT" },
  { name: "mypy", version: ">= 1.9", purpose: "Type checking", license: "MIT" },
  { name: "bandit", version: ">= 1.7", purpose: "Security scan", license: "Apache 2.0" },
  { name: "coverage", version: ">= 7.4", purpose: "Test coverage", license: "Apache 2.0" },
];

function Row({ d }: { d: Dep }) {
  return (
    <tr className="bg-atx-panel">
      <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11.5px] text-atx-accent">
        {d.name}
      </td>
      <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11.5px] text-atx-ink-dim">
        {d.version}
      </td>
      <td className="border-b border-atx-line-soft px-4 py-3 text-[13px] text-atx-ink">
        {d.purpose}
      </td>
      <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11.5px] text-atx-ink-mid">
        {d.license}
      </td>
    </tr>
  );
}

export default function SbomPage() {
  return (
    <section className="mx-auto max-w-[1320px] px-7 py-24">
      <AtxEyebrow>SBOM</AtxEyebrow>
      <h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
        Software bill
        <br />
        <em className="italic text-atx-accent">of materials.</em>
      </h1>
      <p className="mt-8 max-w-[720px] text-[15px] leading-[1.65] text-atx-ink-mid">
        Attestix ships with a pinned dependency tree. Every runtime dependency
        and development dependency is listed below with its licence. A machine
        readable CycloneDX SBOM is published with every GitHub release.
      </p>

      <h2 className="mt-14 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        Runtime dependencies
      </h2>
      <div className="mt-4 overflow-hidden rounded-atx-md border border-atx-line-soft">
        <table className="w-full border-collapse text-left">
          <thead className="bg-atx-bg-sunken">
            <tr>
              <th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                Package
              </th>
              <th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                Version
              </th>
              <th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                Purpose
              </th>
              <th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                Licence
              </th>
            </tr>
          </thead>
          <tbody>
            {RUNTIME.map((d) => (
              <Row key={d.name} d={d} />
            ))}
          </tbody>
        </table>
      </div>

      <h2 className="mt-14 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        Development dependencies
      </h2>
      <div className="mt-4 overflow-hidden rounded-atx-md border border-atx-line-soft">
        <table className="w-full border-collapse text-left">
          <thead className="bg-atx-bg-sunken">
            <tr>
              <th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                Package
              </th>
              <th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                Version
              </th>
              <th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                Purpose
              </th>
              <th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                Licence
              </th>
            </tr>
          </thead>
          <tbody>
            {DEV.map((d) => (
              <Row key={d.name} d={d} />
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
