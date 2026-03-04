"use client";

import { Section } from "@/components/section";
import { BlurFade } from "@/components/ui/blur-fade";
import { cn } from "@/lib/utils";
import {
  FingerprintIcon,
  GlobeIcon,
  CreditCardIcon,
  ShieldCheckIcon,
  GitForkIcon,
  ScaleIcon,
  FileSearchIcon,
  StarIcon,
  LinkIcon,
} from "lucide-react";

const layers = [
  {
    name: "Identity Layer",
    tagline: "Who is this agent?",
    description:
      "did:key and did:web resolution with UAIT bridge connecting MCP, A2A, and DID ecosystems.",
    color: "gold" as const,
    span: "col-span-1 lg:col-span-1",
    href: "https://docs.attestix.io/api-reference/#identity-8-tools",
    modules: [
      { name: "Identity", Icon: FingerprintIcon },
      { name: "DIDs", Icon: GlobeIcon },
      { name: "Agent Cards", Icon: CreditCardIcon },
    ],
  },
  {
    name: "Trust Layer",
    tagline: "What can this agent do?",
    description:
      "W3C Verifiable Credentials with Ed25519 signatures, UCAN delegation chains with scoped permissions, and regulatory compliance tooling for EU AI Act workflows.",
    color: "primary" as const,
    span: "col-span-1 lg:col-span-2",
    href: "https://docs.attestix.io/api-reference/#credentials-8-tools",
    modules: [
      { name: "Credentials", Icon: ShieldCheckIcon },
      { name: "Delegation", Icon: GitForkIcon },
      { name: "Compliance", Icon: ScaleIcon },
    ],
  },
  {
    name: "Observability Layer",
    tagline: "What did this agent do?",
    description:
      "Hash-chained provenance tracking, reputation scoring from verified actions, and blockchain anchoring to Base L2 via EAS for tamper-proof audit trails.",
    color: "gold" as const,
    span: "col-span-1 lg:col-span-3",
    href: "https://docs.attestix.io/api-reference/#provenance-5-tools",
    modules: [
      { name: "Provenance", Icon: FileSearchIcon },
      { name: "Reputation", Icon: StarIcon },
      { name: "Blockchain", Icon: LinkIcon },
    ],
  },
];

export function Architecture() {
  return (
    <Section
      id="architecture"
      title="Architecture"
      subtitle="9 Modules, One Coherent Stack"
    >
      <div className="border-x border-t p-3 md:p-5">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
          {layers.map((layer, idx) => (
            <BlurFade
              key={layer.name}
              delay={0.1 + idx * 0.12}
              inView
              className={layer.span}
            >
              <a
                href={layer.href}
                target="_blank"
                rel="noopener noreferrer"
                className={cn(
                  "group relative flex flex-col gap-4 rounded-xl p-5 h-full",
                  "transform-gpu transition-all duration-300 hover:-translate-y-1",
                  "dark:[border:1px_solid_rgba(255,255,255,.1)] dark:bg-background",
                  "dark:[box-shadow:0_-20px_80px_-20px_#ffffff1f_inset]"
                )}
              >
                {/* Module pills */}
                <div className="flex flex-wrap items-center gap-2">
                  {layer.modules.map((mod) => (
                    <div
                      key={mod.name}
                      className={cn(
                        "flex items-center gap-1.5 rounded-lg border px-3 py-2 text-xs font-medium transition-colors",
                        layer.color === "gold"
                          ? "border-gold/20 bg-gold/5 text-gold group-hover:bg-gold/15 group-hover:border-gold/35"
                          : "border-primary/20 bg-primary/5 text-primary group-hover:bg-primary/15 group-hover:border-primary/35"
                      )}
                    >
                      <mod.Icon className="h-4 w-4" />
                      {mod.name}
                    </div>
                  ))}
                </div>

                {/* Content */}
                <div>
                  <div className="flex items-center gap-2 mb-1.5">
                    <div
                      className={cn(
                        "h-1.5 w-1.5 rounded-full",
                        layer.color === "gold" ? "bg-gold" : "bg-primary"
                      )}
                    />
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                      {layer.tagline}
                    </span>
                  </div>
                  <h3 className="text-base font-semibold text-foreground mb-1">
                    {layer.name}
                  </h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {layer.description}
                  </p>
                </div>

                {/* Hover overlay */}
                <div className="pointer-events-none absolute inset-0 rounded-xl transform-gpu transition-all duration-300 group-hover:bg-black/[.03] group-hover:dark:bg-neutral-800/10" />
              </a>
            </BlurFade>
          ))}
        </div>
      </div>
    </Section>
  );
}
