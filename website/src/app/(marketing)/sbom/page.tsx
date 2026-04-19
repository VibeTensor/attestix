import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";
import Link from "next/link";

export const metadata = constructMetadata({
  title: "SBOM",
  description:
    "Attestix software bill of materials. Mirror of pyproject.toml at the v0.3.0 release. See GitHub for the machine-readable CycloneDX artefact when published.",
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
        prevent silent major-version drift. A machine-readable{" "}
        <strong className="text-atx-ink">CycloneDX 1.5 SBOM</strong> is
        generated by the GitHub Actions{" "}
        <Link
          href="https://github.com/VibeTensor/attestix/actions/workflows/sbom.yml"
          target="_blank"
          rel="noopener noreferrer"
          className="text-atx-accent hover:underline"
        >
          SBOM workflow
        </Link>{" "}
        on every push to main and attached as an asset to every published
        release. The table mirror below is a convenience reference; the
        authoritative artefact is the JSON.
      </p>

      <div className="mt-10 flex flex-col gap-3 rounded-atx-md border border-atx-accent/40 bg-atx-accent-soft p-6 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex-1">
          <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-accent">
            Authoritative artefact
          </div>
          <p className="mt-1 text-[13.5px] leading-[1.55] text-atx-ink">
            Latest release attaches{" "}
            <code className="rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-1.5 py-0.5 font-mono-atx text-[12px] text-atx-accent">
              attestix-sbom.cyclonedx.json
            </code>{" "}
            with a SHA-256 sidecar.
          </p>
        </div>
        <Link
          href="https://github.com/VibeTensor/attestix/releases/latest"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex h-10 items-center justify-center rounded-atx-md bg-atx-accent px-5 text-[13px] font-medium text-[oklch(0.14_0.01_180)] hover:bg-atx-accent-deep"
        >
          Download latest SBOM &rarr;
        </Link>
      </div>

      <DepTable title="Runtime dependencies" deps={RUNTIME} />
      <DepTable title="Optional extras" deps={OPTIONAL} />
      <DepTable title="Development dependencies" deps={DEV} />

      <h2 className="mt-14 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        Reproduce locally
      </h2>
      <p className="mt-3 max-w-[760px] text-[13.5px] leading-[1.6] text-atx-ink-mid">
        The CycloneDX SBOM can be regenerated on any developer machine.
        Install the project with its blockchain extra, install the{" "}
        <code className="rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-1.5 py-0.5 font-mono-atx text-[12px] text-atx-accent">
          sbom
        </code>{" "}
        extra which pulls in the CycloneDX generator, then run:
      </p>
      <pre className="mt-4 overflow-x-auto rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-4 font-mono-atx text-[12px] text-atx-ink">
        {`pip install -e ".[blockchain,sbom]"
cyclonedx-py environment --output-format json \\
  --output-file attestix-sbom.cyclonedx.json
sha256sum attestix-sbom.cyclonedx.json`}
      </pre>
      <p className="mt-3 max-w-[760px] text-[13px] leading-[1.6] text-atx-ink-mid">
        Compare the resulting SHA-256 with the{" "}
        <code className="rounded-atx-xs border border-atx-line-soft bg-atx-bg-sunken px-1.5 py-0.5 font-mono-atx text-[12px] text-atx-accent">
          .sha256
        </code>{" "}
        sidecar attached to the release to verify integrity. The output
        conforms to the{" "}
        <Link
          href="https://cyclonedx.org/docs/1.5/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-atx-accent hover:underline"
        >
          CycloneDX 1.5 specification
        </Link>
        .
      </p>

      <div className="mt-10 rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-6">
        <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
          Security pipeline
        </div>
        <p className="mt-2 text-[13.5px] leading-[1.6] text-atx-ink-mid">
          Every release passes pip-audit, bandit, and safety scans in CI
          before publish. See{" "}
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
