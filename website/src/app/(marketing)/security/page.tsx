import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";
import Link from "next/link";

export const metadata = constructMetadata({
  title: "Security",
  description:
    "Responsible disclosure, security fixes, and vulnerability handling for Attestix.",
});

const DISCLOSURES = [
  {
    id: "ATX-2026-04",
    date: "2026-04-17",
    severity: "HIGH",
    title: "Delegation chain auth bypass",
    fix: "Parent token verification + capability attenuation enforced in UCAN chain.",
    version: "0.3.0",
  },
  {
    id: "ATX-2026-03",
    date: "2026-04-17",
    severity: "HIGH",
    title: "PyJWT CVE mitigation",
    fix: "Pinned PyJWT >= 2.8.1 with dependency lock.",
    version: "0.3.0",
  },
  {
    id: "ATX-2026-02",
    date: "2026-04-17",
    severity: "MEDIUM",
    title: "Server-side request forgery in agent-card fetch",
    fix: "URL allowlist, private-IP block, redirect limit.",
    version: "0.3.0",
  },
  {
    id: "ATX-2026-01",
    date: "2026-04-17",
    severity: "MEDIUM",
    title: "API timing side-channel on credential verify",
    fix: "Constant-time signature comparison.",
    version: "0.3.0",
  },
];

const SEV_STYLE: Record<string, string> = {
  HIGH: "border-atx-err/40 bg-atx-err/[0.08] text-atx-err",
  MEDIUM: "border-atx-warn/40 bg-atx-warn/[0.08] text-atx-warn",
  LOW: "border-atx-info/40 bg-atx-info/[0.08] text-atx-info",
};

export default function SecurityPage() {
  return (
    <section className="mx-auto max-w-[1080px] px-7 py-24">
      <AtxEyebrow>Security</AtxEyebrow>
      <h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
        Responsible
        <br />
        <em className="italic text-atx-accent">disclosure.</em>
      </h1>

      <div className="mt-10 space-y-6 text-[15px] leading-[1.65] text-atx-ink-mid">
        <p>
          Attestix is cryptographic compliance infrastructure. We treat
          vulnerabilities with urgency. If you have found a security issue in
          any Attestix module, MCP tool, REST endpoint, or integration, please
          contact us through a private channel before public disclosure.
        </p>
        <p>
          Email{" "}
          <a
            href="mailto:security@vibetensor.com"
            className="text-atx-accent hover:underline"
          >
            security@vibetensor.com
          </a>{" "}
          with a description, reproduction steps, and your preferred
          attribution. We will acknowledge within 48 hours and provide a
          target resolution timeline within five business days.
        </p>
      </div>

      <h2 className="mt-16 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        Process
      </h2>
      <ol className="mt-3 space-y-2 text-[14px] leading-[1.7] text-atx-ink-mid">
        <li>
          <strong className="text-atx-ink">01.</strong> Report privately.
          Include reproduction, affected version, impact.
        </li>
        <li>
          <strong className="text-atx-ink">02.</strong> We acknowledge in 48 h
          and triage.
        </li>
        <li>
          <strong className="text-atx-ink">03.</strong> We patch, request CVE
          if appropriate, and prepare a release.
        </li>
        <li>
          <strong className="text-atx-ink">04.</strong> Coordinated disclosure
          at release time with credit.
        </li>
      </ol>

      <h2 className="mt-16 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        Recent disclosures
      </h2>
      <div className="mt-6 overflow-hidden rounded-atx-md border border-atx-line-soft">
        <table className="w-full border-collapse text-left text-[13px]">
          <thead className="bg-atx-bg-sunken">
            <tr>
              <th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                ID
              </th>
              <th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                Date
              </th>
              <th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                Severity
              </th>
              <th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                Issue
              </th>
              <th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                Fixed in
              </th>
            </tr>
          </thead>
          <tbody>
            {DISCLOSURES.map((d) => (
              <tr key={d.id} className="bg-atx-panel">
                <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11.5px] text-atx-accent">
                  {d.id}
                </td>
                <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11.5px] text-atx-ink-dim">
                  {d.date}
                </td>
                <td className="border-b border-atx-line-soft px-4 py-3">
                  <span
                    className={`rounded-atx-xs border px-2 py-0.5 font-mono-atx text-[10.5px] uppercase tracking-[0.12em] ${SEV_STYLE[d.severity]}`}
                  >
                    {d.severity}
                  </span>
                </td>
                <td className="border-b border-atx-line-soft px-4 py-3">
                  <div className="text-atx-ink">{d.title}</div>
                  <div className="mt-1 text-[12px] text-atx-ink-mid">
                    {d.fix}
                  </div>
                </td>
                <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11.5px] text-atx-ok">
                  v{d.version}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-10 rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-6">
        <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
          See also
        </div>
        <div className="mt-2 flex flex-wrap gap-4 text-[13.5px]">
          <Link
            href="/sbom"
            className="text-atx-accent hover:underline"
          >
            Software bill of materials
          </Link>
          <Link
            href="/changelog"
            className="text-atx-accent hover:underline"
          >
            Changelog
          </Link>
          <a
            href="https://github.com/VibeTensor/attestix/security"
            target="_blank"
            rel="noopener noreferrer"
            className="text-atx-accent hover:underline"
          >
            GitHub security advisories
          </a>
        </div>
      </div>
    </section>
  );
}
