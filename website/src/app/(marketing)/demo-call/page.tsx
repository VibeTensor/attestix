import Link from "next/link";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "Book a demo",
  description:
    "Book a live walkthrough of Attestix with the VibeTensor team. 30 minutes. Bring your compliance team.",
});

const AGENDA = [
  "Your current compliance workflow and where it breaks",
  "How Attestix identity, credentials, and audit trail map to your articles",
  "Live tour of the console against your agent stack (LangChain, OpenAI Agents SDK, CrewAI)",
  "Integration path and rollout plan",
  "Q and A on enterprise support, SLA, on-premises",
];

const WHO = [
  { role: "Compliance lead", context: "Regulated org subject to EU AI Act" },
  {
    role: "AI engineering lead",
    context: "Shipping autonomous agents in production",
  },
  {
    role: "Security / risk",
    context: "Auditing AI systems and vendor attestations",
  },
  { role: "Policy / legal", context: "Building internal AI governance" },
];

const H3 = "text-[19px] font-semibold tracking-[-0.48px] text-atx-ink";
const LINK =
  "text-atx-accent underline decoration-atx-line underline-offset-4 transition-colors duration-200 hover:decoration-atx-accent";

export default function DemoCallPage() {
  return (
    <>
      <section className="px-6 pb-12 pt-16 text-center md:pt-20">
        <div className="mx-auto max-w-[860px]">
          <AtxEyebrow>Enterprise</AtxEyebrow>
          <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
            Book a <span className="text-atx-accent">live walkthrough.</span>
          </h1>
          <p className="mx-auto mt-5 max-w-[640px] text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
            Thirty minutes with the VibeTensor team, tailored to your agent
            stack and compliance posture. Bring whoever needs to say yes. We
            will not pitch; we will walk through the console end-to-end against
            a workflow you care about.
          </p>
        </div>
      </section>

      <section className="bg-atx-bg pb-20">
        <div className="mx-auto grid w-full max-w-[1200px] gap-8 px-6 lg:grid-cols-[1fr_1.3fr]">
          <div className="space-y-10">
            <div>
              <h2 className={H3}>Agenda</h2>
              <ul className="mt-4 space-y-2.5">
                {AGENDA.map((a) => (
                  <li
                    key={a}
                    className="flex gap-3 text-[15px] leading-[1.6] text-atx-ink-mid"
                  >
                    <span className="mt-2.5 block h-1 w-1 shrink-0 rounded-full bg-atx-accent" />
                    {a}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h2 className={H3}>Who should attend</h2>
              <ul className="mt-4 grid gap-2.5">
                {WHO.map((w) => (
                  <li
                    key={w.role}
                    className="rounded-xl border border-atx-line bg-atx-panel/60 px-4 py-3"
                  >
                    <div className="text-[15px] font-medium text-atx-ink">{w.role}</div>
                    <div className="mt-0.5 text-[13px] text-atx-ink-dim">{w.context}</div>
                  </li>
                ))}
              </ul>
            </div>

            <div className="rounded-2xl border border-atx-line bg-atx-panel/60 p-6">
              <h2 className={H3}>Not ready for a call?</h2>
              <ul className="mt-3 space-y-2 text-[15px] leading-[1.6] text-atx-ink-mid">
                <li>
                  Try the{" "}
                  <Link href="/console" className={LINK}>
                    interactive console
                  </Link>
                </li>
                <li>
                  Install locally with{" "}
                  <code className="rounded-md border border-atx-line-soft bg-atx-bg-sunken px-1.5 py-0.5 font-mono-atx text-[12.5px] text-atx-accent">
                    pip install attestix
                  </code>
                </li>
                <li>
                  Read the{" "}
                  <Link href="/research" className={LINK}>
                    research paper
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          <div className="rounded-2xl border border-atx-line bg-atx-panel p-8">
            <h2 className={H3}>Request a 30-min slot</h2>

            <p className="mt-3 text-[15px] leading-[1.6] text-atx-ink-mid">
              Pick a time that works for your team. Replies land within one
              business day. If you prefer to send the details directly, the
              email link below opens your mail client.
            </p>

            <div className="mt-6 flex flex-wrap gap-3">
              <a
                href="mailto:info@vibetensor.com?subject=Attestix%20demo%20request&body=Please%20reply%20with%20a%20slot%20that%20works%20for%20the%20team.%0A%0ACompany%3A%20%0ARole%3A%20%0AFrameworks%20in%20use%3A%20%0ARisk%20tier%3A%20%0AArticles%20in%20scope%3A%20%0ATimeline%3A%20%0AQuestions%3A%20"
                className="inline-flex items-center gap-2 rounded-full bg-atx-accent px-6 py-3 text-[15px] font-medium text-[oklch(0.14_0.01_180)] transition-colors duration-200 hover:bg-atx-accent-deep"
              >
                Email us &rarr;
              </a>
              <a
                href="https://cal.com/vibetensor/attestix"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center rounded-full border border-atx-line px-6 py-3 text-[15px] font-medium text-atx-ink-mid transition-colors duration-200 hover:border-atx-ink-dim hover:text-atx-ink"
              >
                Open calendar
              </a>
            </div>

            <div className="mt-8 rounded-xl border border-atx-line-soft bg-atx-bg-sunken p-5">
              <p className="text-[13px] font-medium text-atx-ink">Include in your message</p>
              <ul className="mt-2 space-y-1.5 text-[14px] leading-[1.55] text-atx-ink-mid">
                <li>Name and work email</li>
                <li>Company and your role</li>
                <li>Preferred times in your timezone</li>
                <li>Frameworks you ship with (LangChain, OpenAI, CrewAI)</li>
                <li>Risk tier, articles in scope, and target timeline</li>
              </ul>
            </div>

            <p className="pt-5 text-[13px] leading-[1.6] text-atx-ink-dim">
              Direct email:{" "}
              <a
                href="mailto:info@vibetensor.com?subject=Attestix%20demo%20request"
                className={LINK}
              >
                info@vibetensor.com
              </a>
              . We reply within one business day.
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
