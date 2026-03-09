"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
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
  flatMinimumEur: number;
  revenuePercentage: number;
  colorClass: string;
  bgClass: string;
  borderClass: string;
  iconBgClass: string;
}

const FINE_TIERS: FineTier[] = [
  {
    name: "Tier 1",
    article: "Article 5",
    description: "Prohibited AI practices",
    flatMinimumEur: 35_000_000,
    revenuePercentage: 7,
    colorClass: "text-red-400",
    bgClass: "bg-red-500/10",
    borderClass: "border-red-500/30",
    iconBgClass: "bg-red-500/20",
  },
  {
    name: "Tier 2",
    article: "Articles 6-49",
    description: "High-risk non-compliance",
    flatMinimumEur: 15_000_000,
    revenuePercentage: 3,
    colorClass: "text-orange-400",
    bgClass: "bg-orange-500/10",
    borderClass: "border-orange-500/30",
    iconBgClass: "bg-orange-500/20",
  },
  {
    name: "Tier 3",
    article: "Article 99(4)",
    description: "Incorrect information to authorities",
    flatMinimumEur: 7_500_000,
    revenuePercentage: 1,
    colorClass: "text-yellow-400",
    bgClass: "bg-yellow-500/10",
    borderClass: "border-yellow-500/30",
    iconBgClass: "bg-yellow-500/20",
  },
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

function calculateFine(
  revenueUsd: number,
  tier: FineTier
): {
  fineEur: number;
  isPercentageBased: boolean;
  percentageAmount: number;
} {
  const revenueEur = revenueUsd / EUR_USD_RATE;
  const percentageAmount = revenueEur * (tier.revenuePercentage / 100);
  const isPercentageBased = percentageAmount > tier.flatMinimumEur;
  const fineEur = Math.max(tier.flatMinimumEur, percentageAmount);

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
}: {
  tier: FineTier;
  revenueUsd: number;
  hasCalculated: boolean;
}) {
  const { fineEur, isPercentageBased, percentageAmount } = calculateFine(
    revenueUsd,
    tier
  );

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
          value={hasCalculated ? fineEur : tier.flatMinimumEur}
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
                {tier.revenuePercentage}% of revenue ={" "}
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
                Flat minimum = {formatCurrency(tier.flatMinimumEur, "EUR")}
              </span>
            </p>
            <p className="mt-2 pt-2 border-t border-current/10 font-medium text-foreground">
              Applying {isPercentageBased ? "percentage" : "flat minimum"}{" "}
              (whichever is higher)
            </p>
          </>
        ) : (
          <>
            <p>
              {formatCurrency(tier.flatMinimumEur, "EUR")} or{" "}
              {tier.revenuePercentage}% of global annual revenue
            </p>
            <p className="italic">Whichever is higher</p>
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
    <div className="mt-24 pb-16">
      {/* Header */}
      <div className="text-center py-12 px-4">
        <div className="inline-flex items-center gap-2 rounded-full border border-border bg-muted/50 px-4 py-1.5 text-sm text-muted-foreground mb-6">
          <Scale className="h-4 w-4" />
          <span>EU AI Act Fine Calculator</span>
        </div>
        <h1 className="text-3xl font-bold text-foreground sm:text-4xl lg:text-5xl tracking-tight">
          What could non-compliance cost you?
        </h1>
        <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
          The EU AI Act introduces three tiers of fines based on the severity
          of the violation. Enter your company&apos;s revenue to see your
          potential financial exposure.
        </p>
      </div>

      {/* Calculator */}
      <div className="mx-auto max-w-5xl px-4">
        <div className="rounded-xl border border-border bg-card p-6 sm:p-8 mb-8">
          <label
            htmlFor="revenue-input"
            className="block text-sm font-medium text-foreground mb-2"
          >
            Annual global revenue (USD)
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
              className="w-full rounded-lg border border-input bg-background pl-8 pr-4 py-3 text-lg font-mono text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:ring-offset-background transition-colors"
              aria-label="Annual global revenue in USD"
            />
          </div>

          {/* Preset buttons */}
          <div className="flex flex-wrap gap-2">
            {PRESETS.map((preset) => (
              <button
                key={preset.value}
                onClick={() => handlePresetClick(preset)}
                className={cn(
                  "rounded-md border px-3 py-1.5 text-sm font-medium transition-all",
                  activePreset === preset.value
                    ? "border-primary bg-primary text-primary-foreground"
                    : "border-border bg-muted/50 text-muted-foreground hover:border-primary/50 hover:text-foreground"
                )}
              >
                {preset.label}
              </button>
            ))}
          </div>

          {hasCalculated && (
            <p className="mt-3 text-xs text-muted-foreground">
              Using approximate conversion rate: 1 EUR = {EUR_USD_RATE} USD.
              Fines are assessed in euros.
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
                  Enforcement begins
                </h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                August 2, 2026. Prohibited AI practice provisions already
                apply since February 2025. Full enforcement for high-risk
                systems follows.
              </p>
            </div>

            {/* SME note */}
            <div className="rounded-lg border border-border bg-card p-5">
              <div className="flex items-center gap-2 mb-3">
                <Calculator className="h-4 w-4 text-primary" />
                <h3 className="text-sm font-semibold text-foreground">
                  SMEs and startups
                </h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                SMEs and startups get proportionate fines, but the flat
                minimums still apply. A company with EUR 5M revenue faces the
                same EUR 35M Tier 1 minimum as a multinational.
              </p>
            </div>
          </div>
        </div>

        {/* CTA section */}
        <div className="rounded-xl border border-primary/20 bg-primary/5 p-8 text-center">
          <h2 className="text-2xl font-bold text-foreground mb-3">
            Reduce your exposure
          </h2>
          <p className="text-muted-foreground mb-6 max-w-xl mx-auto">
            Attestix automates EU AI Act compliance documentation, risk
            classification, and audit trails. Start building your compliance
            posture before enforcement begins.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            <Link href="/docs/getting-started">
              <Button size="lg">
                Start automating compliance
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/docs/guides/eu-ai-act-compliance">
              <Button variant="outline" size="lg">
                EU compliance walkthrough
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
