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

const H2 = "text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink";
const LINK =
  "text-atx-ink underline decoration-atx-line underline-offset-4 transition-colors duration-200 hover:decoration-atx-ink-dim";
const CODE =
  "rounded-md border border-atx-line-soft bg-atx-bg-sunken px-1.5 py-0.5 font-mono-atx text-[13px] text-atx-accent";
const TH = "border-b border-atx-line-soft px-4 py-3.5 text-[13px] font-medium text-atx-ink-dim";

function Row({ d }: { d: Dep }) {
  return (
    <tr className="bg-atx-panel/60">
      <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[13px] text-atx-accent">
        {d.name}
      </td>
      <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[13px] text-atx-ink-dim">
        {d.version}
      </td>
      <td className="border-b border-atx-line-soft px-4 py-3 text-[14px] leading-[1.5] text-atx-ink-mid">
        {d.purpose}
      </td>
      <td className="border-b border-atx-line-soft px-4 py-3 text-[13px] text-atx-ink-mid">
        {d.license}
      </td>
    </tr>
  );
}

function DepTable({ title, deps }: { title: string; deps: Dep[] }) {
  return (
    <div className="mt-14 first:mt-0">
      <h3 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
        {title}
      </h3>
      <div className="mt-4 overflow-x-auto rounded-2xl border border-atx-line">
        <table className="w-full min-w-[720px] border-collapse text-left">
          <thead className="bg-atx-bg-sunken">
            <tr>
              <th className={TH}>Package</th>
              <th className={TH}>Version constraint</th>
              <th className={TH}>Purpose</th>
              <th className={TH}>Licence</th>
            </tr>
          </thead>
          <tbody>
            {deps.map((d) => (
              <Row key={d.name} d={d} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function SbomPage() {
  return (
    <>
      <section className="bg-atx-bg px-6 pb-16 pt-16 md:pt-20">
        <div className="mx-auto max-w-[860px] text-center">
          <AtxEyebrow>SBOM</AtxEyebrow>
          <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
            Software bill <span className="text-atx-accent">of materials.</span>
          </h1>
          <p className="mx-auto mt-5 max-w-[640px] text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
            Attestix pins every runtime dependency with lower and upper bounds to
            prevent silent major-version drift. A machine-readable{" "}
            <strong className="font-medium text-atx-ink">CycloneDX 1.5 SBOM</strong> is
            generated by the GitHub Actions{" "}
            <Link
              href="https://github.com/VibeTensor/attestix/actions/workflows/sbom.yml"
              target="_blank"
              rel="noopener noreferrer"
              className={LINK}
            >
              SBOM workflow
            </Link>{" "}
            on every push to main and attached as an asset to every published
            release. The table mirror below is a convenience reference; the
            authoritative artefact is the JSON.
          </p>
        </div>

        <div className="mx-auto mt-12 flex max-w-[840px] flex-col gap-5 rounded-2xl border border-atx-accent/30 bg-atx-accent/[0.05] p-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex-1">
            <p className="text-[14px] font-medium text-atx-accent">Authoritative artefact</p>
            <p className="mt-1.5 text-[15px] leading-[1.6] text-atx-ink-mid">
              Latest release attaches{" "}
              <code className={CODE}>attestix-sbom.cyclonedx.json</code>{" "}
              with a SHA-256 sidecar.
            </p>
          </div>
          <Link
            href="https://github.com/VibeTensor/attestix/releases/latest"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex shrink-0 items-center justify-center rounded-full bg-atx-accent px-6 py-3 text-[15px] font-medium text-[oklch(0.14_0.01_180)] transition-colors duration-200 hover:bg-atx-accent-deep"
          >
            Download latest SBOM &rarr;
          </Link>
        </div>
      </section>

      <section className="bg-atx-bg-elev py-20">
        <div className="mx-auto w-full max-w-[1200px] px-6">
          <h2 className={`${H2} text-center`}>Dependencies</h2>
          <div className="mt-10">
            <DepTable title="Runtime dependencies" deps={RUNTIME} />
            <DepTable title="Optional extras" deps={OPTIONAL} />
            <DepTable title="Development dependencies" deps={DEV} />
          </div>
        </div>
      </section>

      <section className="bg-atx-bg py-20">
        <div className="mx-auto w-full max-w-[720px] px-6">
          <h2 className={`${H2} text-center`}>Reproduce locally</h2>
          <p className="mt-4 text-[15px] leading-[1.6] text-atx-ink-mid">
            The CycloneDX SBOM can be regenerated on any developer machine.
            Install the project with its blockchain extra, install the{" "}
            <code className={CODE}>sbom</code>{" "}
            extra which pulls in the CycloneDX generator, then run:
          </p>
          <pre className="mt-5 overflow-x-auto rounded-xl bg-atx-bg-sunken p-6 font-mono-atx text-[13px] leading-[1.9] text-atx-ink">
            {`pip install -e ".[blockchain,sbom]"
cyclonedx-py environment --output-format json \\
  --output-file attestix-sbom.cyclonedx.json
sha256sum attestix-sbom.cyclonedx.json`}
          </pre>
          <p className="mt-5 text-[15px] leading-[1.6] text-atx-ink-mid">
            Compare the resulting SHA-256 with the{" "}
            <code className={CODE}>.sha256</code>{" "}
            sidecar attached to the release to verify integrity. The output
            conforms to the{" "}
            <Link
              href="https://cyclonedx.org/docs/1.5/"
              target="_blank"
              rel="noopener noreferrer"
              className={LINK}
            >
              CycloneDX 1.5 specification
            </Link>
            .
          </p>

          <div className="mt-10 rounded-2xl border border-atx-line bg-atx-panel/60 p-6">
            <h3 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
              Security pipeline
            </h3>
            <p className="mt-2 text-[15px] leading-[1.6] text-atx-ink-mid">
              Every release passes pip-audit, bandit, and safety scans in CI
              before publish. See{" "}
              <Link href="/security" className={LINK}>
                /security
              </Link>{" "}
              for the vulnerability disclosure log.
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
