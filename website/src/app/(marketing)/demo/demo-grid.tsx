"use client";

import { MagicCard } from "@/components/ui/magic-card";
import { BlurFade } from "@/components/ui/blur-fade";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Shield, Calculator, Fingerprint, BarChart3, ArrowRight } from "lucide-react";
import Link from "next/link";
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
    <div className="container mx-auto px-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
        {demos.map((demo, index) => (
          <BlurFade key={demo.href} delay={0.1 + index * 0.1} inView>
            <Link href={demo.href} className="block h-full group">
              <MagicCard
                className="h-full rounded-xl border border-border transition-transform duration-300 group-hover:scale-[1.02]"
                gradientColor="#4F46E520"
                gradientFrom="#4F46E5"
                gradientTo="#818CF8"
                gradientSize={250}
                gradientOpacity={0.15}
              >
                <div className="p-6 flex flex-col gap-4 h-full">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                      <demo.icon className="h-5 w-5" />
                    </div>
                    <h2 className="text-lg font-semibold text-foreground">
                      {demo.title}
                    </h2>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed flex-1">
                    {demo.description}
                  </p>
                  <div className="flex items-center gap-1.5 text-sm font-medium text-primary transition-colors group-hover:text-primary/80">
                    Try it
                    <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </div>
                </div>
              </MagicCard>
            </Link>
          </BlurFade>
        ))}
      </div>

      {/* Bottom CTA */}
      <BlurFade delay={0.6} inView>
        <div className="mt-16 text-center">
          <p className="text-lg text-muted-foreground mb-6">
            Ready to implement these for real?
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/docs/getting-started"
              className={cn(
                buttonVariants({ variant: "default", size: "lg" }),
                "rounded-lg font-medium"
              )}
            >
              Get Started
            </Link>
            <Link
              href="/docs"
              className={cn(
                buttonVariants({ variant: "outline", size: "lg" }),
                "rounded-lg font-medium"
              )}
            >
              Read the Docs
            </Link>
          </div>
        </div>
      </BlurFade>
    </div>
  );
}
