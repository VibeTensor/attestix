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

export default function DemoCallPage() {
  return (
    <section className="mx-auto max-w-[1320px] px-7 py-24">
      <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
        <div>
          <AtxEyebrow>Enterprise</AtxEyebrow>
          <h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
            Book a
            <br />
            <em className="italic text-atx-accent">live walkthrough.</em>
          </h1>
        </div>
        <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
          Thirty minutes with the VibeTensor team, tailored to your agent
          stack and compliance posture. Bring whoever needs to say yes. We
          will not pitch; we will walk through the console end-to-end against
          a workflow you care about.
        </p>
      </div>

      <div className="mt-14 grid gap-8 lg:grid-cols-[1fr_1.3fr]">
        <div className="space-y-8">
          <div>
            <div className="font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
              Agenda
            </div>
            <ul className="mt-3 space-y-2">
              {AGENDA.map((a) => (
                <li
                  key={a}
                  className="flex gap-3 text-[13.5px] leading-[1.6] text-atx-ink-mid"
                >
                  <span className="mt-2 block h-1 w-1 shrink-0 rounded-full bg-atx-accent" />
                  {a}
                </li>
              ))}
            </ul>
          </div>

          <div>
            <div className="font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
              Who should attend
            </div>
            <ul className="mt-3 grid gap-2">
              {WHO.map((w) => (
                <li
                  key={w.role}
                  className="rounded-atx-sm border border-atx-line-soft bg-atx-panel px-4 py-3"
                >
                  <div className="font-mono-atx text-[12.5px] text-atx-ink">
                    {w.role}
                  </div>
                  <div className="mt-0.5 text-[12px] text-atx-ink-dim">
                    {w.context}
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-5">
            <div className="font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
              Not ready for a call?
            </div>
            <ul className="mt-2 space-y-1 text-[13px] text-atx-ink-mid">
              <li>
                Try the{" "}
                <Link
                  href="/console"
                  className="text-atx-accent hover:underline"
                >
                  interactive console
                </Link>
              </li>
              <li>
                Install locally with{" "}
                <code className="rounded-atx-xs border border-atx-line-soft bg-atx-panel px-1.5 py-0.5 font-mono-atx text-[11.5px] text-atx-accent">
                  pip install attestix
                </code>
              </li>
              <li>
                Read the{" "}
                <Link
                  href="/research"
                  className="text-atx-accent hover:underline"
                >
                  research paper
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="rounded-atx-md border border-atx-line-soft bg-atx-panel p-7">
          <div className="font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
            Request a 30-min slot
          </div>

          <p className="mt-4 text-[13.5px] leading-[1.6] text-atx-ink-mid">
            Pick a time that works for your team. Replies land within one
            business day. If you prefer to send the details directly, the
            email link below opens your mail client.
          </p>

          <div className="mt-6 flex flex-wrap gap-3">
            <a
              href="mailto:info@vibetensor.com?subject=Attestix%20demo%20request&body=Please%20reply%20with%20a%20slot%20that%20works%20for%20the%20team.%0A%0ACompany%3A%20%0ARole%3A%20%0AFrameworks%20in%20use%3A%20%0ARisk%20tier%3A%20%0AArticles%20in%20scope%3A%20%0ATimeline%3A%20%0AQuestions%3A%20"
              className="inline-flex h-10 items-center gap-2 rounded-atx-md bg-atx-accent px-5 text-[13px] font-medium text-[oklch(0.14_0.01_180)] transition-colors hover:bg-atx-accent-deep"
            >
              Email us &rarr;
            </a>
            <a
              href="https://cal.com/vibetensor/attestix"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex h-10 items-center rounded-atx-md border border-atx-line px-5 text-[13px] font-medium text-atx-ink transition-colors hover:border-atx-ink-dim hover:bg-atx-bg-sunken"
            >
              Open calendar
            </a>
          </div>

          <div className="mt-8 space-y-2 rounded-atx-sm border border-atx-line-soft bg-atx-bg-sunken p-4">
            <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
              Include in your message
            </div>
            <ul className="space-y-1 font-mono-atx text-[11.5px] text-atx-ink-mid">
              <li>Name and work email</li>
              <li>Company and your role</li>
              <li>Preferred times in your timezone</li>
              <li>Frameworks you ship with (LangChain, OpenAI, CrewAI)</li>
              <li>Risk tier, articles in scope, and target timeline</li>
            </ul>
          </div>

          <p className="pt-5 text-[12px] leading-[1.55] text-atx-ink-dim">
            Direct email:{" "}
            <a
              href="mailto:info@vibetensor.com?subject=Attestix%20demo%20request"
              className="text-atx-accent hover:underline"
            >
              info@vibetensor.com
            </a>
            . We reply within one business day.
          </p>
        </div>
      </div>
    </section>
  );
}

