import Link from "next/link";
import {
  Shield,
  Calculator,
  Fingerprint,
  BarChart3,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

interface DemoCard {
  title: string;
  description: string;
  href: string;
  icon: LucideIcon;
}

const demos: DemoCard[] = [
  {
    title: "EU AI Act Compliance Checker",
    description:
      "Find out your AI system's risk classification under the EU AI Act in 60 seconds.",
    href: "/demo/compliance-checker",
    icon: Shield,
  },
  {
    title: "Fine Calculator",
    description:
      "Calculate your potential EU AI Act fine based on your company's annual revenue.",
    href: "/demo/fine-calculator",
    icon: Calculator,
  },
  {
    title: "Agent Identity Explorer",
    description:
      "See what a verifiable AI agent identity looks like. Create a sample identity and explore every field.",
    href: "/demo/identity-explorer",
    icon: Fingerprint,
  },
  {
    title: "Reputation Dashboard",
    description:
      "Explore how AI agents earn and lose trust through a live reputation scoring dashboard.",
    href: "/demo/reputation-dashboard",
    icon: BarChart3,
  },
];

export function DemoGrid() {
  return (
    <>
      <div className="grid gap-5 md:grid-cols-2">
        {demos.map((demo, i) => (
          <Link
            key={demo.href}
            href={demo.href}
            className="group flex flex-col gap-4 rounded-atx-md border border-atx-line-soft bg-atx-panel p-6 transition-colors hover:border-atx-accent/60 hover:bg-atx-panel-hi"
          >
            <div className="flex items-center justify-between font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-faint">
              <span>{String(i + 1).padStart(2, "0")} / 04</span>
              <span className="text-atx-accent transition-transform group-hover:translate-x-0.5">
                &rarr;
              </span>
            </div>
            <div className="text-[28px] text-atx-accent">
              <demo.icon className="h-7 w-7" />
            </div>
            <h2 className="font-serif text-[22px] leading-tight text-atx-ink">
              {demo.title}
            </h2>
            <p className="text-[13.5px] leading-[1.55] text-atx-ink-mid">
              {demo.description}
            </p>
          </Link>
        ))}
      </div>

      <div className="mt-14 flex flex-col items-start gap-4 rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-8 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
            Next
          </div>
          <p className="mt-2 font-serif text-[22px] leading-tight text-atx-ink">
            Ready to ship this for real?
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <Link
            href="/docs/getting-started"
            className="inline-flex h-10 items-center rounded-atx-md bg-atx-accent px-5 text-[13px] font-medium text-[oklch(0.14_0.01_180)] transition-colors hover:bg-atx-accent-deep"
          >
            Get started
          </Link>
          <Link
            href="/docs"
            className="inline-flex h-10 items-center rounded-atx-md border border-atx-line px-5 text-[13px] font-medium text-atx-ink transition-colors hover:border-atx-ink-dim hover:bg-atx-panel"
          >
            Read the docs
          </Link>
        </div>
      </div>
    </>
  );
}
