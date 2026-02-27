"use client";

import { Section } from "@/components/section";
import { Button } from "@/components/ui/button";
import { CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { siteConfig } from "@/lib/config";
import { cn } from "@/lib/utils";
import { Check } from "lucide-react";

function PricingTier({
  tier,
}: {
  tier: (typeof siteConfig.pricing)[0];
}) {
  const isEnterprise = tier.name === "Enterprise";

  return (
    <div
      className="outline-focus transition-transform-background relative z-10 box-border grid h-full w-full overflow-hidden text-foreground motion-reduce:transition-none lg:border-r border-t last:border-r-0"
    >
      <div className="flex flex-col h-full">
        <CardHeader className="border-b p-4 grid grid-rows-2 h-fit">
          <CardTitle className="flex items-center justify-between">
            <span className="text-sm font-medium text-muted-foreground">
              {tier.name}
            </span>
          </CardTitle>
          <div className="pt-2 text-3xl font-bold">
            {tier.price.monthly}
            {tier.price.monthly !== "Custom" && (
              <span className="text-sm font-medium text-muted-foreground">
                {" "}/ {tier.frequency.monthly}
              </span>
            )}
          </div>
          <p className="text-[15px] font-medium text-muted-foreground">
            {tier.description}
          </p>
        </CardHeader>

        <CardContent className="flex-grow p-4 pt-5">
          <ul className="space-y-2">
            {tier.features.map((feature, featureIndex) => (
              <li key={featureIndex} className="flex items-center">
                <Check className="mr-2 size-4 text-primary" />
                <span className="font-medium">{feature}</span>
              </li>
            ))}
          </ul>
        </CardContent>

        <Button
          size="lg"
          className={cn(
            "w-full rounded-none shadow-none",
            isEnterprise
              ? "bg-muted text-foreground hover:bg-muted/80"
              : "bg-primary text-primary-foreground hover:bg-primary/90"
          )}
          asChild
        >
          <a
            href={
              isEnterprise
                ? "mailto:info@vibetensor.com?subject=Attestix Enterprise"
                : "https://docs.attestix.vibetensor.com/getting-started/"
            }
            target={isEnterprise ? undefined : "_blank"}
            rel={isEnterprise ? undefined : "noopener noreferrer"}
          >
            {tier.cta}
          </a>
        </Button>
      </div>
    </div>
  );
}

export function Pricing() {
  return (
    <Section id="pricing" title="Pricing">
      <div className="border border-b-0 grid grid-rows-1">
        <div className="grid grid-rows-1 gap-y-10 p-10">
          <div className="text-center">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tighter text-balance">
              Open source, free forever.
            </h2>

            <p className="mt-6 text-balance text-muted-foreground">
              Attestix is <strong>Apache 2.0 licensed</strong> with all 47 tools available
              for free. Enterprise support available for organizations with
              advanced compliance requirements.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2">
          {siteConfig.pricing.map((tier, index) => (
            <PricingTier key={index} tier={tier} />
          ))}
        </div>
      </div>
    </Section>
  );
}
