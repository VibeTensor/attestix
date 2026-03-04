"use client";

import { Section } from "@/components/section";
import { BlurFade } from "@/components/ui/blur-fade";
import { cn } from "@/lib/utils";
import {
  ShieldCheckIcon,
  FingerprintIcon,
  GitForkIcon,
  ScaleIcon,
  FileSearchIcon,
  LinkIcon,
  KeyIcon,
  FileCodeIcon,
  NetworkIcon,
  HashIcon,
  LockIcon,
  ContactIcon,
  HexagonIcon,
  MonitorIcon,
  MousePointerClickIcon,
  CodeIcon,
  WindIcon,
  TerminalIcon,
  BookOpenIcon,
} from "lucide-react";

interface TechItem {
  name: string;
  label: string;
  Icon: typeof ShieldCheckIcon;
  color: "primary" | "gold";
}

const categories: { title: string; description: string; items: TechItem[] }[] = [
  {
    title: "Standards & Protocols",
    description: "Built on open specifications",
    items: [
      { name: "W3C VCs", label: "W3C Verifiable Credentials", Icon: ShieldCheckIcon, color: "primary" },
      { name: "W3C DIDs", label: "W3C Decentralized Identifiers", Icon: FingerprintIcon, color: "gold" },
      { name: "UCAN", label: "UCAN Delegation", Icon: GitForkIcon, color: "primary" },
      { name: "Ed25519", label: "Ed25519 (RFC 8032)", Icon: KeyIcon, color: "gold" },
      { name: "EU AI Act", label: "EU AI Act Compliance", Icon: ScaleIcon, color: "primary" },
      { name: "MCP", label: "Model Context Protocol", Icon: NetworkIcon, color: "gold" },
      { name: "A2A", label: "Agent-to-Agent Protocol", Icon: ContactIcon, color: "primary" },
      { name: "IETF", label: "IETF Standards", Icon: BookOpenIcon, color: "gold" },
      { name: "JSON-LD", label: "JSON-LD Context", Icon: FileCodeIcon, color: "primary" },
      { name: "JWT", label: "JSON Web Tokens", Icon: LockIcon, color: "gold" },
      { name: "DID:key", label: "DID Key Method", Icon: FileSearchIcon, color: "primary" },
      { name: "EAS", label: "Ethereum Attestation Service", Icon: HashIcon, color: "gold" },
    ],
  },
  {
    title: "MCP Clients",
    description: "First-class support in every major AI IDE",
    items: [
      { name: "Claude Desktop", label: "Claude Desktop", Icon: MonitorIcon, color: "gold" },
      { name: "Cursor", label: "Cursor IDE", Icon: MousePointerClickIcon, color: "gold" },
      { name: "Continue", label: "Continue", Icon: CodeIcon, color: "gold" },
      { name: "Windsurf", label: "Windsurf", Icon: WindIcon, color: "gold" },
      { name: "VS Code", label: "VS Code", Icon: TerminalIcon, color: "gold" },
    ],
  },
  {
    title: "Blockchain",
    description: "On-chain anchoring and verification",
    items: [
      { name: "Base L2", label: "Base L2", Icon: LinkIcon, color: "gold" },
      { name: "Ethereum", label: "Ethereum", Icon: HexagonIcon, color: "gold" },
      { name: "EAS", label: "Ethereum Attestation Service", Icon: HashIcon, color: "gold" },
    ],
  },
];

export function TechStack() {
  return (
    <Section
      id="tech-stack"
      title="Technology Stack"
      subtitle="Standards, Clients, and Infrastructure"
    >
      <div className="border-x border-t">
        {categories.map((category, catIdx) => (
          <BlurFade key={category.title} delay={0.1 + catIdx * 0.1} inView>
            <div className={cn(catIdx < categories.length - 1 && "border-b")}>
              <div className="flex items-center gap-3 px-4 py-2.5 border-b">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                  {category.title}
                </span>
                <span className="hidden sm:inline text-[11px] text-muted-foreground/50">
                  {category.description}
                </span>
              </div>
              <div
                className={cn(
                  "grid",
                  category.items.length <= 3
                    ? "grid-cols-3"
                    : category.items.length === 5
                      ? "grid-cols-2 sm:grid-cols-3 md:grid-cols-5"
                      : "grid-cols-3 sm:grid-cols-4 md:grid-cols-6"
                )}
              >
                {category.items.map((item, idx) => (
                  <div
                    key={`${category.title}-${item.name}`}
                    className={cn(
                      "group flex flex-col items-center justify-center gap-2 py-6 px-3 transition-colors hover:bg-secondary/20",
                      "border-b",
                      "border-r",
                      "[&:nth-child(3n)]:border-r-0 sm:[&:nth-child(3n)]:border-r",
                      category.items.length <= 3 && "[&:nth-child(3n)]:border-r-0",
                      category.items.length === 5 && "sm:[&:nth-child(3n)]:border-r-0 md:[&:nth-child(3n)]:border-r md:[&:nth-child(5n)]:border-r-0",
                      category.items.length > 5 && "sm:[&:nth-child(4n)]:border-r-0 md:[&:nth-child(4n)]:border-r md:[&:nth-child(6n)]:border-r-0",
                    )}
                    title={item.label}
                  >
                    <div
                      className={cn(
                        "flex h-10 w-10 items-center justify-center rounded-lg transition-all duration-200",
                        item.color === "gold"
                          ? "bg-gold/10 text-gold group-hover:bg-gold/20 group-hover:shadow-[0_0_16px_oklch(0.76_0.155_73_/_0.2)]"
                          : "bg-primary/10 text-primary group-hover:bg-primary/20 group-hover:shadow-[0_0_16px_oklch(0.46_0.24_264_/_0.2)]"
                      )}
                    >
                      <item.Icon className="h-5 w-5" />
                    </div>
                    <span className="text-xs font-medium text-muted-foreground group-hover:text-foreground transition-colors text-center">
                      {item.name}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </BlurFade>
        ))}
      </div>
    </Section>
  );
}
