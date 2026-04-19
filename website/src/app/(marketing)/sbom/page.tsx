import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";
import Link from "next/link";

export const metadata = constructMetadata({
  title: "SBOM",
  description:
    "Attestix software bill of materials. Mirror of pyproject.toml plus the authoritative CycloneDX SBOM published with every GitHub release.",
});

interface Dep {
  name: string;
  version: string;
  purpose: string;
  license: string;
}

// Runtime dependencies mirrored from pyproject.toml (v0.3.0).
// Authoritative SBOM is published with every GitHub release as CycloneDX.
const RUNTIME: Dep[] = [
  {
    name: "mcp[cli]",
    version: ">= 1.8.0, < 2.0.0",
    purpose: "Model Context Protocol runtime and CLI",
    license: "MIT",
  },
  {
    name: "cryptography",
    version: ">= 46.0.7, < 47.0.0",
    purpose:
      "Ed25519, PBKDF2, SHA-256 (CVE-2026-34073, CVE-2026-39892 fixes)",
    license: "Apache 2.0 / BSD",
  },
  {
    name: "PyJWT[crypto]",
    version: ">= 2.12.0, < 3.0.0",
    purpose:
      "UCAN JWT sign and verify (CVE-2026-32597 crit header fix)",
    license: "MIT",
  },
  {
    name: "base58",
    version: ">= 2.1.1, < 3.0.0",
    purpose: "Base58 encoding for DID key methods",
    license: "MIT",
  },
  {
    name: "httpx",
    version: ">= 0.28.0, < 0.30.0",
    purpose: "did:web resolution, remote verify, agent discovery",
    license: "BSD-3",
  },
  {
    name: "python-dotenv",
    version: ">= 1.1.0, < 2.0.0",
    purpose: "Environment variable loading",
    license: "BSD-3",
  },
  {
    name: "nest-asyncio",
    version: ">= 1.6.0, < 2.0.0",
    purpose: "Nested event-loop support",
    license: "BSD-2",
  },
  {
    name: "python-json-logger",
    version: ">= 3.3.0, < 5.0.0",
    purpose: "Structured JSON logging",
    license: "BSD-2",
  },
  {
    name: "filelock",
    version: ">= 3.13.0, < 4.0.0",
    purpose: "File-based concurrency locking",
    license: "Unlicense",
  },
  {
    name: "click",
    version: ">= 8.1.0, < 9.0.0",
    purpose: "CLI framework",
    license: "BSD-3",
  },
  {
    name: "python-multipart",
    version: ">= 0.0.26, < 0.1.0",
    purpose:
      "Multipart parser (pinned >= 0.0.26 for CVE-2026-40347 DoS fix)",
    license: "Apache 2.0",
  },
];

const OPTIONAL: Dep[] = [
  {
    name: "web3",
    version: ">= 7.0.0, < 8.0.0",
    purpose: "EAS anchoring to Base L2 testnet (blockchain extra)",
    license: "MIT",
  },
  {
    name: "weasyprint",
    version: ">= 62.0",
    purpose: "PDF report generation (reports extra)",
    license: "BSD-3",
  },
];

const DEV: Dep[] = [
  {
    name: "pytest",
    version: ">= 8.0",
    purpose: "Test runner",
    license: "MIT",
  },
  {
    name: "pytest-asyncio",
    version: ">= 0.24",
    purpose: "Async test support",
    license: "Apache 2.0",
  },
  {
    name: "pytest-cov",
    version: ">= 5.0",
    purpose: "Coverage plugin",
    license: "MIT",
  },
  {
    name: "respx",
    version: ">= 0.22",
    purpose: "HTTP mocking for httpx",
    license: "BSD-3",
  },
  {
    name: "ruff",
    version: ">= 0.6.0",
    purpose: "Lint and format",
    license: "MIT",
  },
  {
    name: "mypy",
    version: ">= 1.11",
    purpose: "Type checking",
    license: "MIT",
  },
  {
    name: "pip-audit",
    version: ">= 2.7",
    purpose: "Dependency vulnerability audit",
    license: "Apache 2.0",
  },
  {
    name: "bandit",
    version: ">= 1.7",
    purpose: "SAST on Python source",
    license: "Apache 2.0",
  },
  {
    name: "safety",
    version: ">= 3.2",
    purpose: "CVE scan (advisory)",
    license: "MIT",
  },
  {
    name: "build",
    version: ">= 1.2",
    purpose: "PEP 517 wheel builder",
    license: "MIT",
  },
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

function DepTable({ title, deps }: { title: string; deps: Dep[] }) {
  return (
    <>
      <h2 className="mt-14 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        {title}
      </h2>
      <div className="mt-4 overflow-hidden rounded-atx-md border border-atx-line-soft">
        <table className="w-full border-collapse text-left">
          <thead className="bg-atx-bg-sunken">
            <tr>
              <th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                Package
              </th>
              <th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                Version constraint
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
            {deps.map((d) => (
              <Row key={d.name} d={d} />
            ))}
          </tbody>
        </table>
      </div>
    </>
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
      <p className="mt-8 max-w-[760px] text-[15px] leading-[1.65] text-atx-ink-mid">
        Attestix pins every runtime dependency with lower and upper bounds to
        prevent silent major-version drift. The tables below mirror{" "}
        <Link
          href="https://github.com/VibeTensor/attestix/blob/main/pyproject.toml"
          target="_blank"
          rel="noopener noreferrer"
          className="text-atx-accent hover:underline"
        >
          pyproject.toml
        </Link>{" "}
        at the v0.3.0 release. For the authoritative machine-readable SBOM
        (CycloneDX), see the{" "}
        <Link
          href="https://github.com/VibeTensor/attestix/releases"
          target="_blank"
          rel="noopener noreferrer"
          className="text-atx-accent hover:underline"
        >
          GitHub release artefacts
        </Link>
        .
      </p>

      <DepTable title="Runtime dependencies" deps={RUNTIME} />
      <DepTable title="Optional extras" deps={OPTIONAL} />
      <DepTable title="Development dependencies" deps={DEV} />

      <div className="mt-10 rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-6">
        <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
          Reproducibility
        </div>
        <p className="mt-2 text-[13.5px] leading-[1.6] text-atx-ink-mid">
          Every release goes through pip-audit and safety scans in CI before
          publish. See{" "}
          <Link
            href="/security"
            className="text-atx-accent hover:underline"
          >
            /security
          </Link>{" "}
          for the vulnerability disclosure log.
        </p>
      </div>
    </section>
  );
}
