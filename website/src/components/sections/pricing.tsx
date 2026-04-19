import Link from "next/link";
import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { siteConfig } from "@/lib/config";

type Tier = (typeof siteConfig.pricing)[number];

function PricingTier({ tier }: { tier: Tier }) {
  const isEnterprise = tier.name === "Enterprise";
  const href = isEnterprise ? "/demo-call" : "/docs/getting-started";

  return (
    <div
      className={`relative flex flex-col rounded-atx-md border p-8 transition-colors ${
        isEnterprise
          ? "border-atx-line bg-atx-panel-hi"
          : "border-atx-accent/50 bg-atx-panel"
      }`}
    >
      <div className="flex items-center justify-between font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        <span>{tier.name}</span>
        {!isEnterprise && (
          <span className="rounded-atx-xs border border-atx-accent/40 bg-atx-accent-soft px-2 py-0.5 text-atx-accent">
            open source
          </span>
        )}
      </div>

      <div className="mt-5 flex items-baseline gap-2">
        <div className="font-serif text-[48px] leading-none text-atx-ink">
          {tier.price.monthly}
        </div>
        <div className="font-mono-atx text-[11px] uppercase tracking-[0.1em] text-atx-ink-dim">
          {tier.frequency.monthly}
        </div>
      </div>

      <p className="mt-3 text-[13.5px] leading-[1.6] text-atx-ink-mid">
        {tier.description}
      </p>

      <ul className="mt-7 space-y-2.5">
        {tier.features.map((feature) => (
          <li
            key={feature}
            className="flex gap-3 text-[13.5px] leading-[1.55] text-atx-ink-mid"
          >
            <span className="mt-1.5 block h-1 w-1 shrink-0 rounded-full bg-atx-accent" />
            {feature}
          </li>
        ))}
      </ul>

      <Link
        href={href}
        className={`mt-8 inline-flex h-10 items-center justify-center rounded-atx-md px-5 text-[13px] font-medium transition-colors ${
          isEnterprise
            ? "border border-atx-line text-atx-ink hover:border-atx-ink-dim hover:bg-atx-bg-sunken"
            : "bg-atx-accent text-[oklch(0.14_0.01_180)] hover:bg-atx-accent-deep"
        }`}
      >
        {tier.cta}
      </Link>
    </div>
  );
}

export function Pricing() {
  return (
    <section className="mx-auto max-w-[1320px] px-7 py-24">
      <div className="grid items-start gap-10 lg:grid-cols-[1fr_1.2fr]">
        <div>
          <AtxEyebrow>Pricing</AtxEyebrow>
          <h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
            Open source.
            <br />
            <em className="italic text-atx-accent">Apache 2.0.</em>
          </h1>
        </div>
        <p className="text-[15px] leading-[1.65] text-atx-ink-mid">
          The complete attestation toolkit for AI agents. Everything you need
          is in the open-source release. Enterprise support is available for
          organisations with advanced compliance requirements, on-premises
          deployment, or custom SLAs.
        </p>
      </div>

      <div className="mt-14 grid gap-6 md:grid-cols-2">
        {siteConfig.pricing.map((tier) => (
          <PricingTier key={tier.name} tier={tier} />
        ))}
      </div>
    </section>
  );
}
