"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import {
  AlertTriangle,
  ArrowRight,
  Calculator,
  CalendarClock,
  Info,
  Scale,
  ShieldAlert,
  TrendingUp,
} from "lucide-react";
import { useInView, useMotionValue, useSpring } from "motion/react";

// Fixed EUR/USD rate (approximate)
const EUR_USD_RATE = 1.08;

interface FineTier {
  name: string;
  article: string;
  description: string;
  capEur: number;
  revenuePercentage: number;
  /** Art. 99(6a): small mid-caps get the lower-of rule for this tier. */
  smcLowerOf: boolean;
  colorClass: string;
  bgClass: string;
  borderClass: string;
  iconBgClass: string;
}

const FINE_TIERS: FineTier[] = [
  {
    name: "Tier 1",
    article: "Article 99(3)",
    description: "Prohibited AI practices (Article 5)",
    capEur: 35_000_000,
    revenuePercentage: 7,
    smcLowerOf: false,
    colorClass: "text-red-400",
    bgClass: "bg-red-500/10",
    borderClass: "border-red-500/30",
    iconBgClass: "bg-red-500/20",
  },
  {
    name: "Tier 2",
    article: "Article 99(4)",
    description: "High-risk, operator, and transparency obligations",
    capEur: 15_000_000,
    revenuePercentage: 3,
    smcLowerOf: true,
    colorClass: "text-orange-400",
    bgClass: "bg-orange-500/10",
    borderClass: "border-orange-500/30",
    iconBgClass: "bg-orange-500/20",
  },
  {
    name: "Tier 3",
    article: "Article 99(5)",
    description: "Incorrect information to authorities",
    capEur: 7_500_000,
    revenuePercentage: 1,
    smcLowerOf: true,
    colorClass: "text-yellow-400",
    bgClass: "bg-yellow-500/10",
    borderClass: "border-yellow-500/30",
    iconBgClass: "bg-yellow-500/20",
  },
];

const SIZES: { value: CompanySize; label: string; note: string }[] = [
  { value: "large", label: "Large enterprise", note: "The higher of the fixed amount and the turnover percentage applies to every tier." },
  { value: "smc", label: "Small mid-cap", note: "Art. 99(6a): the lower amount applies to tiers 2 and 3; tier 1 (prohibited practices) stays higher-of." },
  { value: "sme", label: "SME or start-up", note: "Art. 99(6): the lower amount applies to every tier." },
];

interface PresetOption {
  label: string;
  value: number;
}

const PRESETS: PresetOption[] = [
  { label: "$1M", value: 1_000_000 },
  { label: "$5M", value: 5_000_000 },
  { label: "$10M", value: 10_000_000 },
  { label: "$50M", value: 50_000_000 },
  { label: "$100M", value: 100_000_000 },
  { label: "$500M", value: 500_000_000 },
  { label: "$1B", value: 1_000_000_000 },
];

function formatCurrency(
  amount: number,
  currency: "EUR" | "USD" = "EUR"
): string {
  const formatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
  return formatter.format(amount);
}

function formatInputValue(value: string): string {
  const digits = value.replace(/[^0-9]/g, "");
  if (!digits) return "";
  const num = parseInt(digits, 10);
  return new Intl.NumberFormat("en-US").format(num);
}

function parseInputValue(value: string): number {
  const digits = value.replace(/[^0-9]/g, "");
  if (!digits) return 0;
  return parseInt(digits, 10);
}

type CompanySize = "large" | "smc" | "sme";

// Art. 99(3)-(5): the fixed amount and the turnover percentage are both
// ceilings ("up to"); the higher applies. Art. 99(6): SMEs and start-ups get
// the lower, for every tier. Art. 99(6a), added by Regulation (EU) 2026/1744:
// small mid-caps get the lower for 99(4) and 99(5) only, not 99(3).
function usesLowerOf(size: CompanySize, tier: FineTier): boolean {
  return size === "sme" || (size === "smc" && tier.smcLowerOf);
}

function calculateFine(
  revenueUsd: number,
  tier: FineTier,
  size: CompanySize
): {
  fineEur: number;
  isPercentageBased: boolean;
  percentageAmount: number;
} {
  const revenueEur = revenueUsd / EUR_USD_RATE;
  const percentageAmount = revenueEur * (tier.revenuePercentage / 100);
  const fineEur = usesLowerOf(size, tier)
    ? Math.min(tier.capEur, percentageAmount)
    : Math.max(tier.capEur, percentageAmount);
  const isPercentageBased = fineEur === percentageAmount;

  return { fineEur, isPercentageBased, percentageAmount };
}

// Animated EUR counter component
function AnimatedFineAmount({
  value,
  className,
}: {
  value: number;
  className?: string;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const motionValue = useMotionValue(0);
  const springValue = useSpring(motionValue, {
    damping: 40,
    stiffness: 90,
  });
  const isInView = useInView(ref, { once: false, margin: "0px" });
  const prevValueRef = useRef(0);

  useEffect(() => {
    if (isInView && value !== prevValueRef.current) {
      motionValue.set(value);
      prevValueRef.current = value;
    }
  }, [motionValue, isInView, value]);

  useEffect(
    () =>
      springValue.on("change", (latest) => {
        if (ref.current) {
          ref.current.textContent = formatCurrency(
            Math.round(latest),
            "EUR"
          );
        }
      }),
    [springValue]
  );

  return (
    <span ref={ref} className={cn("inline-block tabular-nums", className)}>
      {formatCurrency(value, "EUR")}
    </span>
  );
}

function FineCard({
  tier,
  revenueUsd,
  hasCalculated,
  size,
}: {
  tier: FineTier;
  revenueUsd: number;
  hasCalculated: boolean;
  size: CompanySize;
}) {
  const { fineEur, isPercentageBased, percentageAmount } = calculateFine(
    revenueUsd,
    tier,
    size
  );
  const rule = !usesLowerOf(size, tier)
    ? "whichever is higher"
    : size === "sme"
      ? "whichever is lower, Art. 99(6)"
      : "whichever is lower, Art. 99(6a)";

  return (
    <div
      className={cn(
        "rounded-lg border p-6 transition-all duration-300",
        tier.borderClass,
        tier.bgClass,
        hasCalculated
          ? "opacity-100 translate-y-0"
          : "opacity-60 translate-y-1"
      )}
    >
      <div className="flex items-center gap-3 mb-4">
        <div className={cn("rounded-md p-2", tier.iconBgClass)}>
          {tier.name === "Tier 1" && (
            <ShieldAlert className={cn("h-5 w-5", tier.colorClass)} />
          )}
          {tier.name === "Tier 2" && (
            <AlertTriangle className={cn("h-5 w-5", tier.colorClass)} />
          )}
          {tier.name === "Tier 3" && (
            <Info className={cn("h-5 w-5", tier.colorClass)} />
          )}
        </div>
        <div>
          <h3 className={cn("font-semibold text-lg", tier.colorClass)}>
            {tier.name}
          </h3>
          <p className="text-xs text-muted-foreground">{tier.article}</p>
        </div>
      </div>

      <p className="text-sm text-muted-foreground mb-4">{tier.description}</p>

      <div className="mb-3">
        <AnimatedFineAmount
          value={hasCalculated ? fineEur : tier.capEur}
          className={cn("text-3xl font-bold tracking-tight", tier.colorClass)}
        />
      </div>

      <div className="space-y-1.5 text-xs text-muted-foreground">
        {hasCalculated ? (
          <>
            <p className="flex items-center gap-1.5">
              <span
                className={cn(
                  "inline-block w-1.5 h-1.5 rounded-full",
                  isPercentageBased
                    ? "bg-current opacity-100"
                    : "bg-muted-foreground/30"
                )}
              />
              <span
                className={
                  isPercentageBased ? "text-foreground font-medium" : ""
                }
              >
                {tier.revenuePercentage}% of turnover ={" "}
                {formatCurrency(percentageAmount, "EUR")}
              </span>
            </p>
            <p className="flex items-center gap-1.5">
              <span
                className={cn(
                  "inline-block w-1.5 h-1.5 rounded-full",
                  !isPercentageBased
                    ? "bg-current opacity-100"
                    : "bg-muted-foreground/30"
                )}
              />
              <span
                className={
                  !isPercentageBased ? "text-foreground font-medium" : ""
                }
              >
                Fixed cap = {formatCurrency(tier.capEur, "EUR")}
              </span>
            </p>
            <p className="mt-2 pt-2 border-t border-current/10 font-medium text-foreground">
              Maximum fine uses the {isPercentageBased ? "percentage" : "fixed cap"}{" "}
              ({rule})
            </p>
          </>
        ) : (
          <>
            <p>
              {formatCurrency(tier.capEur, "EUR")} or{" "}
              {tier.revenuePercentage}% of global annual revenue
            </p>
            <p className="italic">Up to, {rule}</p>
          </>
        )}
      </div>
    </div>
  );
}

export function FineCalculator() {
  const [inputValue, setInputValue] = useState("");
  const [revenueUsd, setRevenueUsd] = useState(0);
  const [hasCalculated, setHasCalculated] = useState(false);
  const [activePreset, setActivePreset] = useState<number | null>(null);
  const [size, setSize] = useState<CompanySize>("large");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleCalculate = useCallback((value: number) => {
    setRevenueUsd(value);
    setHasCalculated(value > 0);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatInputValue(e.target.value);
    setInputValue(formatted);
    setActivePreset(null);

    const parsed = parseInputValue(e.target.value);
    handleCalculate(parsed);
  };

  const handlePresetClick = (preset: PresetOption) => {
    setActivePreset(preset.value);
    setInputValue(new Intl.NumberFormat("en-US").format(preset.value));
    handleCalculate(preset.value);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const parsed = parseInputValue(inputValue);
      handleCalculate(parsed);
    }
  };

  return (
    <div className="pb-20 pt-16">
      {/* Header */}
      <div className="px-6 pb-12 text-center">
        <p className="text-[14px] font-medium text-atx-accent">EU AI Act fine calculator</p>
        <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
          What could non-compliance cost you?
        </h1>
        <p className="mx-auto mt-5 max-w-[640px] text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
          Article 99 sets three tiers of maximum fines. Enter your worldwide
          annual turnover and company size to see the ceiling for each tier.
        </p>
      </div>

      {/* Calculator */}
      <div className="mx-auto max-w-[1080px] px-6">
        <div className="mb-8 rounded-2xl border border-atx-line bg-atx-panel/60 p-6 sm:p-8">
          <label
            htmlFor="revenue-input"
            className="block text-sm font-medium text-foreground mb-2"
          >
            Worldwide annual turnover (USD)
          </label>

          <div className="relative mb-4">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground font-medium">
              $
            </span>
            <input
              ref={inputRef}
              id="revenue-input"
              type="text"
              inputMode="numeric"
              value={inputValue}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Enter revenue or select a preset below"
              className="w-full rounded-xl border border-atx-line bg-atx-bg-sunken py-3.5 pl-8 pr-4 text-[18px] text-atx-ink transition-colors placeholder:text-atx-ink-faint focus:border-atx-accent focus:outline-none"
              aria-label="Worldwide annual turnover in USD"
            />
          </div>

          {/* Preset buttons */}
          <div className="flex flex-wrap gap-2">
            {PRESETS.map((preset) => (
              <button
                key={preset.value}
                onClick={() => handlePresetClick(preset)}
                className={cn(
                  "rounded-full border px-4 py-1.5 text-[14px] font-medium transition-colors duration-200",
                  activePreset === preset.value
                    ? "border-atx-accent bg-atx-accent text-[oklch(0.14_0.01_180)]"
                    : "border-atx-line text-atx-ink-mid hover:border-atx-ink-dim hover:text-atx-ink"
                )}
              >
                {preset.label}
              </button>
            ))}
          </div>

          <fieldset className="mt-6">
            <legend className="mb-2 text-[14px] font-medium text-atx-ink">Company size</legend>
            <div className="flex flex-wrap gap-2">
              {SIZES.map((o) => (
                <button
                  key={o.value}
                  type="button"
                  aria-pressed={size === o.value}
                  onClick={() => setSize(o.value)}
                  className={cn(
                    "rounded-full border px-4 py-1.5 text-[14px] font-medium transition-colors duration-200",
                    size === o.value
                      ? "border-atx-accent bg-atx-accent/15 text-atx-accent"
                      : "border-atx-line text-atx-ink-mid hover:border-atx-ink-dim hover:text-atx-ink"
                  )}
                >
                  {o.label}
                </button>
              ))}
            </div>
            <p className="mt-2 text-[13px] text-atx-ink-dim">
              {SIZES.find((o) => o.value === size)?.note}
            </p>
          </fieldset>

          {hasCalculated && (
            <p className="mt-4 text-[13px] text-atx-ink-dim">
              Using an approximate rate of 1 EUR = {EUR_USD_RATE} USD; fines are
              set in euros. These are the Article 99 maximums: authorities set
              actual fines case by case under Article 99(7). Not legal advice.
            </p>
          )}
        </div>

        {/* Fine tier cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
          {FINE_TIERS.map((tier) => (
            <FineCard
              key={tier.name}
              tier={tier}
              revenueUsd={revenueUsd}
              hasCalculated={hasCalculated}
              size={size}
            />
          ))}
        </div>

        {/* Context section */}
        <div className="space-y-4 mb-12">
          <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-muted-foreground" />
            Context
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* GDPR comparison */}
            <div className="rounded-lg border border-border bg-card p-5">
              <div className="flex items-center gap-2 mb-3">
                <Scale className="h-4 w-4 text-primary" />
                <h3 className="text-sm font-semibold text-foreground">
                  For comparison
                </h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                GDPR&apos;s largest fine was EUR 1.2B (Meta, 2023). EU AI Act
                fines can exceed this for large organizations operating
                prohibited AI systems.
              </p>
            </div>

            {/* Enforcement date */}
            <div className="rounded-lg border border-border bg-card p-5">
              <div className="flex items-center gap-2 mb-3">
                <CalendarClock className="h-4 w-4 text-primary" />
                <h3 className="text-sm font-semibold text-foreground">
                  Key dates
                </h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Prohibitions since 2 Feb 2025; penalties chapter since 2 Aug
                2025; general application and Article 50 transparency since
                2 Aug 2026. High-risk requirements: Annex III from 2 Dec 2027,
                Annex I from 2 Aug 2028 (Regulation (EU) 2026/1744).
              </p>
            </div>

            {/* SME note */}
            <div className="rounded-lg border border-border bg-card p-5">
              <div className="flex items-center gap-2 mb-3">
                <Calculator className="h-4 w-4 text-primary" />
                <h3 className="text-sm font-semibold text-foreground">
                  SMEs, start-ups, and small mid-caps
                </h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                SMEs and start-ups face the lower of the fixed amount and the
                turnover percentage for every tier (Art. 99(6)): with EUR 5M
                turnover, at most EUR 350,000 for a tier 1 breach, not EUR 35M.
                Small mid-caps get the same lower-of rule for tiers 2 and 3 only
                (Art. 99(6a), Regulation (EU) 2026/1744).
              </p>
            </div>
          </div>
        </div>

        {/* CTA section */}
        <div className="rounded-2xl border border-atx-accent/30 bg-atx-accent/[0.05] p-8 text-center">
          <h2 className="text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink">
            Keep the evidence before anyone asks
          </h2>
          <p className="mx-auto mb-6 mt-3 max-w-xl text-[15.5px] leading-[1.6] text-atx-ink-mid">
            Attestix records the identity, risk classification, and audit
            evidence your EU AI Act documentation needs, so it exists before
            anyone asks for it.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            <Link
              href="/docs/getting-started"
              className="inline-flex items-center gap-2 rounded-full bg-atx-accent px-6 py-3 text-[15px] font-medium text-[oklch(0.14_0.01_180)] transition-colors duration-200 hover:bg-atx-accent-deep"
            >
              Get started <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/docs/guides/eu-ai-act-compliance"
              className="inline-flex items-center rounded-full border border-atx-line px-6 py-3 text-[15px] font-medium text-atx-ink-mid transition-colors duration-200 hover:border-atx-ink-dim hover:text-atx-ink"
            >
              EU AI Act guide
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
