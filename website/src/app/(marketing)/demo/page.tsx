import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { constructMetadata } from "@/lib/utils";

export const metadata = constructMetadata({
  title: "Demos",
  description:
    "Try Attestix in the browser: the interactive console, an EU AI Act fine calculator, a risk classifier, an agent identity explorer, and a reputation dashboard. Data is simulated.",
});

const DEMOS = [
  {
    href: "/console",
    name: "Console",
    body: "The full Attestix workspace: agents, credentials, delegations, and the hash-chained audit trail.",
  },
  {
    href: "/demo/fine-calculator",
    name: "EU AI Act fine calculator",
    body: "Article 99 maximum fines for your turnover and company size, including the SME and small mid-cap rules.",
  },
  {
    href: "/demo/compliance-checker",
    name: "Risk classifier",
    body: "Answer a few questions to see which EU AI Act risk tier an AI system likely falls into.",
  },
  {
    href: "/demo/identity-explorer",
    name: "Agent identity explorer",
    body: "Create a simulated agent identity and inspect every field, from the DID to the trust score.",
  },
  {
    href: "/demo/reputation-dashboard",
    name: "Reputation dashboard",
    body: "How Attestix scores agent reputation from interactions and compliance records.",
  },
];

export default function DemosPage() {
  return (
    <section className="mx-auto max-w-[1200px] px-6 pb-20 pt-16">
      <div className="text-center">
        <p className="text-[14px] font-medium text-atx-accent">Demos</p>
        <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
          Try Attestix in your browser
        </h1>
        <p className="mx-auto mt-5 max-w-[620px] text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
          Interactive previews. Nothing to install and nothing uploaded; data is
          simulated. <code className="font-mono-atx text-[15px] text-atx-accent">pip install attestix</code> for the real thing.
        </p>
      </div>
      <div className="mt-14 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {DEMOS.map((d, i) => (
          <Link
            key={d.href}
            href={d.href}
            className={`group rounded-2xl border p-6 transition-colors duration-200 ${
              i === 0
                ? "border-atx-accent/30 bg-atx-accent/[0.05] hover:border-atx-accent/60"
                : "border-atx-line bg-atx-panel/60 hover:border-atx-ink-dim"
            }`}
          >
            <h2 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">{d.name}</h2>
            <p className="mt-2 text-[15px] leading-[1.55] text-atx-ink-mid">{d.body}</p>
            <span className="mt-5 inline-flex items-center gap-1.5 text-[14px] font-medium text-atx-ink-mid transition-colors group-hover:text-atx-ink">
              Open <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
            </span>
          </Link>
        ))}
      </div>
    </section>
  );
}
