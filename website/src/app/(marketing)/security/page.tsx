import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";
import Link from "next/link";

export const metadata = constructMetadata({
  title: "Security",
  description:
    "Responsible disclosure, security fixes, and vulnerability handling for Attestix.",
});

// ATX-* are internal tracking IDs, not CVE IDs. Dates reflect when the
// fix landed on main. All four shipped together in the v0.3.0 security
// batch after coordinated internal review. Upstream dependency CVEs are
// linked directly; project-scoped findings are tracked internally and
// will be promoted to CVE IDs when disclosed externally.
const DISCLOSURES = [
  {
    id: "ATX-2026-04",
    date: "2026-04-17",
    severity: "HIGH",
    title: "Delegation chain auth bypass",
    fix: "Parent token verification + capability attenuation enforced in UCAN chain.",
    version: "0.3.0",
    reference: null,
  },
  {
    id: "ATX-2026-03",
    date: "2026-04-15",
    severity: "HIGH",
    title: "PyJWT upstream CVE mitigation",
    fix: "Pinned PyJWT >= 2.12.0 with dependency lock.",
    version: "0.3.0",
    reference:
      "https://github.com/jpadilla/pyjwt/security/advisories",
  },
  {
    id: "ATX-2026-02",
    date: "2026-04-10",
    severity: "MEDIUM",
    title: "Server-side request forgery in agent-card fetch",
    fix: "URL allowlist, private-IP block, redirect limit.",
    version: "0.3.0",
    reference: null,
  },
  {
    id: "ATX-2026-01",
    date: "2026-04-02",
    severity: "MEDIUM",
    title: "API timing side-channel on credential verify",
    fix: "Constant-time signature comparison.",
    version: "0.3.0",
    reference: null,
  },
];

const SEV_STYLE: Record<string, string> = {
  HIGH: "bg-atx-err/15 text-atx-err",
  MEDIUM: "bg-atx-warn/15 text-atx-warn",
  LOW: "bg-atx-info/15 text-atx-info",
};

const H2 = "text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink";
const LINK =
  "text-atx-ink underline decoration-atx-line underline-offset-4 transition-colors duration-200 hover:decoration-atx-ink-dim";
const TH = "border-b border-atx-line-soft px-4 py-3.5 text-[13px] font-medium text-atx-ink-dim";

const PROCESS: { n: string; body: string }[] = [
  { n: "01.", body: "Report privately. Include reproduction, affected version, impact." },
  { n: "02.", body: "We acknowledge in 48 h and triage." },
  { n: "03.", body: "We patch, request CVE if appropriate, and prepare a release." },
  { n: "04.", body: "Coordinated disclosure at release time with credit." },
];

export default function SecurityPage() {
  return (
    <>
      <section className="bg-atx-bg px-6 pb-16 pt-16 text-center md:pt-20">
        <div className="mx-auto max-w-[860px]">
          <AtxEyebrow>Security</AtxEyebrow>
          <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
            Responsible <span className="text-atx-accent">disclosure.</span>
          </h1>
          <div className="mx-auto mt-5 max-w-[640px] space-y-4 text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
            <p>
              Attestix is cryptographic compliance infrastructure. We treat
              vulnerabilities with urgency. If you have found a security issue in
              any Attestix module, MCP tool, REST endpoint, or integration, please
              contact us through a private channel before public disclosure.
            </p>
            <p>
              Email{" "}
              <a href="mailto:security@vibetensor.com" className={LINK}>
                security@vibetensor.com
              </a>{" "}
              with a description, reproduction steps, and your preferred
              attribution. We will acknowledge within 48 hours and provide a
              target resolution timeline within five business days.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-atx-bg-elev py-20">
        <div className="mx-auto w-full max-w-[1200px] px-6">
          <h2 className={`${H2} text-center`}>Process</h2>
          <ol className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {PROCESS.map((step) => (
              <li
                key={step.n}
                className="rounded-2xl border border-atx-line bg-atx-panel/60 p-6"
              >
                <span className="text-[14px] font-medium text-atx-accent">{step.n}</span>
                <p className="mt-2 text-[15px] leading-[1.6] text-atx-ink-mid">{step.body}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="bg-atx-bg py-20">
        <div className="mx-auto w-full max-w-[1200px] px-6">
          <div className="text-center">
            <h2 className={H2}>Recent disclosures</h2>
            <p className="mx-auto mt-4 max-w-[720px] text-[15px] leading-[1.6] text-atx-ink-mid">
              ATX-* are internal tracking IDs assigned during the coordinated fix
              cycle, not CVE numbers. Upstream dependency fixes link to the
              upstream advisory. Project-scoped findings are promoted to CVE
              assignments when disclosed externally.
            </p>
          </div>
          <div className="mt-10 overflow-x-auto rounded-2xl border border-atx-line">
            <table className="w-full min-w-[720px] border-collapse text-left text-[14px]">
              <thead className="bg-atx-bg-sunken">
                <tr>
                  <th className={TH}>ID</th>
                  <th className={TH}>Date</th>
                  <th className={TH}>Severity</th>
                  <th className={TH}>Issue</th>
                  <th className={TH}>Fixed in</th>
                </tr>
              </thead>
              <tbody>
                {DISCLOSURES.map((d) => (
                  <tr key={d.id} className="bg-atx-panel/60">
                    <td className="border-b border-atx-line-soft px-4 py-3.5 font-mono-atx text-[13px] text-atx-accent">
                      {d.id}
                    </td>
                    <td className="border-b border-atx-line-soft px-4 py-3.5 font-mono-atx text-[13px] text-atx-ink-dim">
                      {d.date}
                    </td>
                    <td className="border-b border-atx-line-soft px-4 py-3.5">
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-[12px] font-medium ${SEV_STYLE[d.severity]}`}
                      >
                        {d.severity}
                      </span>
                    </td>
                    <td className="border-b border-atx-line-soft px-4 py-3.5">
                      <div className="font-medium text-atx-ink">{d.title}</div>
                      <div className="mt-1 text-[13px] leading-[1.5] text-atx-ink-mid">
                        {d.fix}
                      </div>
                    </td>
                    <td className="border-b border-atx-line-soft px-4 py-3.5 font-mono-atx text-[13px] text-atx-ok">
                      v{d.version}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mx-auto mt-10 max-w-[840px] rounded-2xl border border-atx-line bg-atx-panel/60 p-6 text-center">
            <p className="text-[14px] font-medium text-atx-ink-mid">See also</p>
            <div className="mt-3 flex flex-wrap justify-center gap-x-6 gap-y-2 text-[15px]">
              <Link href="/sbom" className={LINK}>
                Software bill of materials
              </Link>
              <Link href="/changelog" className={LINK}>
                Changelog
              </Link>
              <a
                href="https://github.com/VibeTensor/attestix/security"
                target="_blank"
                rel="noopener noreferrer"
                className={LINK}
              >
                GitHub security advisories
              </a>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
