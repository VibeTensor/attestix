import Link from "next/link";
import { HeroCert } from "./hero-cert";
import { HeroStats } from "./hero-stats";
import { AtxCountdown } from "@/components/atx/atx-countdown";
import { siteConfig } from "@/lib/config";

export function HeroV2() {
  return (
    <section className="relative mx-auto max-w-[1320px] px-7 pt-12 pb-24">
      <div className="mb-10 inline-flex flex-wrap items-center gap-3 rounded-atx-sm border border-atx-line-soft bg-atx-bg-sunken px-3.5 py-2 font-mono-atx text-[11.5px] text-atx-ink-mid">
        <span className="inline-block h-1.5 w-1.5 rounded-full bg-atx-err" />
        <span>
          Enforcement in <AtxCountdown /> &middot; Fines up to &euro;35M or 7%
          global revenue
        </span>
      </div>
      <div className="grid items-start gap-14 lg:grid-cols-[1.15fr_1fr]">
        <div>
          <h1 className="font-serif text-[clamp(44px,6.2vw,88px)] font-normal leading-[1.02] tracking-[-0.015em] text-atx-ink">
            Cryptographic{" "}
            <em className="italic text-atx-accent">proof</em>
            <br />
            your AI agents
            <br />
            are compliant.
          </h1>

          <p className="mt-8 max-w-[560px] text-[16px] leading-[1.6] text-atx-ink-mid">
            Attestix is attestation infrastructure for autonomous AI agents.
            Open-source identity, W3C Verifiable Credentials, EU AI Act
            compliance automation, and reputation scoring. Machine-readable
            evidence your agent can present to a regulator, another agent, or a
            system.
          </p>

          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link
              href="/console"
              className="group inline-flex h-10 items-center gap-2 rounded-atx-md bg-atx-accent px-5 text-[13px] font-medium text-[oklch(0.14_0.01_180)] transition-colors hover:bg-atx-accent-deep"
            >
              Launch console
              <span className="font-mono-atx transition-transform group-hover:translate-x-0.5">
                &rarr;
              </span>
            </Link>
            <a
              href="#workflow"
              className="inline-flex h-10 items-center rounded-atx-md border border-atx-line px-5 text-[13px] font-medium text-atx-ink transition-colors hover:border-atx-ink-dim hover:bg-atx-panel"
            >
              See compliance workflow
            </a>
          </div>

          <div className="mt-8 flex flex-wrap items-center gap-4">
            <code className="rounded-atx-sm border border-atx-line-soft bg-atx-bg-sunken px-3 py-1.5 font-mono-atx text-[12px] text-atx-ink-dim">
              <span className="text-atx-accent">$</span> pip install attestix
            </code>
            <span className="font-mono-atx text-[11px] uppercase tracking-[0.1em] text-atx-ink-faint">
              v{siteConfig.version} &middot; apache 2.0
            </span>
          </div>
        </div>

        <HeroCert />
      </div>

      <HeroStats />
    </section>
  );
}
