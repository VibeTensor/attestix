"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import { AnimatePresence, motion, useSpring, useMotionValue } from "motion/react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { cn } from "@/lib/utils";
import {
  ArrowRight,
  CheckCircle2,
  Copy,
  ExternalLink,
  Fingerprint,
  Key,
  Shield,
  ShieldCheck,
  Star,
  UserCheck,
  Award,
  FileCheck,
  TrendingUp,
} from "lucide-react";

// --- Types ---

type RiskLevel = "minimal" | "limited" | "high";

interface AgentFormState {
  name: string;
  description: string;
  capabilities: Set<string>;
  issuerOrg: string;
  riskLevel: RiskLevel;
}

interface AgentIdentity {
  agent_id: string;
  did: string;
  display_name: string;
  description: string;
  issuer: {
    name: string;
    did: string;
  };
  capabilities: string[];
  created_at: string;
  source_protocol: string;
  risk_level: RiskLevel;
  reputation_score: number;
  signature: string;
  revoked: boolean;
}

// --- Constants ---

const CAPABILITIES = [
  { id: "data_analysis", label: "Data Analysis" },
  { id: "reporting", label: "Reporting" },
  { id: "code_generation", label: "Code Generation" },
  { id: "content_creation", label: "Content Creation" },
  { id: "customer_support", label: "Customer Support" },
  { id: "medical_diagnosis", label: "Medical Diagnosis" },
  { id: "financial_advisory", label: "Financial Advisory" },
  { id: "translation", label: "Translation" },
] as const;

const RISK_LEVELS: { value: RiskLevel; label: string; color: string }[] = [
  { value: "minimal", label: "Minimal", color: "text-atx-ok" },
  { value: "limited", label: "Limited", color: "text-atx-warn" },
  { value: "high", label: "High", color: "text-orange-400" },
];

// --- Utility functions ---

function generateHex(length: number): string {
  const chars = "0123456789abcdef";
  let result = "";
  for (let i = 0; i < length; i++) {
    result += chars[Math.floor(Math.random() * chars.length)];
  }
  return result;
}

function generateBase58Like(length: number): string {
  const chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
  let result = "";
  for (let i = 0; i < length; i++) {
    result += chars[Math.floor(Math.random() * chars.length)];
  }
  return result;
}

function generateBase64Url(length: number): string {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
  let result = "";
  for (let i = 0; i < length; i++) {
    result += chars[Math.floor(Math.random() * chars.length)];
  }
  return result;
}

function generateIdentity(form: AgentFormState): AgentIdentity {
  const agentHex = generateHex(16);
  const didKey = generateBase58Like(44);
  const issuerDidKey = generateBase58Like(44);
  const signature = generateBase64Url(64);
  const targetScore = 0.5 + Math.random() * 0.35;

  return {
    agent_id: `attestix:${agentHex}`,
    did: `did:key:z6Mk${didKey}`,
    display_name: form.name,
    description: form.description,
    issuer: {
      name: form.issuerOrg,
      did: `did:key:z6Mk${issuerDidKey}`,
    },
    capabilities: Array.from(form.capabilities),
    created_at: new Date().toISOString(),
    source_protocol: "manual",
    risk_level: form.riskLevel,
    reputation_score: Math.round(targetScore * 100) / 100,
    signature,
    revoked: false,
  };
}

// --- Components ---

function TrustScoreRing({
  score,
  size = 120,
}: {
  score: number;
  size?: number;
}) {
  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const motionValue = useMotionValue(0);
  const springValue = useSpring(motionValue, {
    damping: 30,
    stiffness: 60,
    mass: 1,
  });
  const [displayValue, setDisplayValue] = useState(0);
  const svgRef = useRef<SVGCircleElement>(null);

  useEffect(() => {
    motionValue.set(score);
  }, [score, motionValue]);

  useEffect(() => {
    const unsubscribe = springValue.on("change", (latest) => {
      setDisplayValue(Math.round(latest * 100) / 100);
      if (svgRef.current) {
        const offset = circumference - latest * circumference;
        svgRef.current.style.strokeDashoffset = `${offset}`;
      }
    });
    return unsubscribe;
  }, [springValue, circumference]);

  const scoreColor =
    displayValue >= 0.7
      ? "#059669"
      : displayValue >= 0.5
        ? "#E1A32C"
        : "#ef4444";

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="-rotate-90">
        {/* Background ring */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-atx-line-soft"
        />
        {/* Progress ring */}
        <circle
          ref={svgRef}
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={scoreColor}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference}
          className="transition-colors duration-500"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-[28px] font-normal tracking-[-0.03em] text-atx-ink tabular-nums">
          {displayValue.toFixed(2)}
        </span>
        <span className="text-[13px] text-atx-ink-dim">Trust score</span>
      </div>
    </div>
  );
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [text]);

  return (
    <button
      onClick={handleCopy}
      className="ml-2 inline-flex items-center text-atx-ink-dim transition-colors duration-200 hover:text-atx-ink"
      title="Copy to clipboard"
      type="button"
    >
      {copied ? (
        <CheckCircle2 className="h-3.5 w-3.5 text-atx-ok" />
      ) : (
        <Copy className="h-3.5 w-3.5" />
      )}
    </button>
  );
}

function RiskBadge({ level }: { level: RiskLevel }) {
  const config = {
    minimal: {
      label: "Minimal risk",
      className: "bg-atx-ok/15 text-atx-ok border-atx-ok/30",
    },
    limited: {
      label: "Limited risk",
      className: "bg-atx-warn/15 text-atx-warn border-atx-warn/30",
    },
    high: {
      label: "High risk",
      className: "bg-orange-500/15 text-orange-400 border-orange-500/30",
    },
  };

  const { label, className } = config[level];

  return (
    <span className={cn("inline-flex items-center rounded-full border px-3 py-0.5 text-[13px] font-medium", className)}>
      {label}
    </span>
  );
}

function ConfigurationForm({
  formState,
  onSubmit,
  onUpdate,
}: {
  formState: AgentFormState;
  onSubmit: () => void;
  onUpdate: (updates: Partial<AgentFormState>) => void;
}) {
  const toggleCapability = (capId: string) => {
    const next = new Set(formState.capabilities);
    if (next.has(capId)) {
      next.delete(capId);
    } else {
      next.add(capId);
    }
    onUpdate({ capabilities: next });
  };

  const canSubmit =
    formState.name.trim().length > 0 &&
    formState.issuerOrg.trim().length > 0 &&
    formState.capabilities.size > 0;

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="agent-name" className="text-[14px] font-medium text-atx-ink">Agent name</Label>
        <Input
          id="agent-name"
          placeholder="e.g., Data Analysis Bot"
          value={formState.name}
          onChange={(e) => onUpdate({ name: e.target.value })}
          className="rounded-xl border-atx-line bg-atx-bg-sunken text-[15px] text-atx-ink placeholder:text-atx-ink-faint"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="agent-description" className="text-[14px] font-medium text-atx-ink">Description</Label>
        <textarea
          id="agent-description"
          placeholder="e.g., Analyzes quarterly financial data"
          value={formState.description}
          onChange={(e) => onUpdate({ description: e.target.value })}
          rows={3}
          className="flex w-full resize-none rounded-xl border border-atx-line bg-atx-bg-sunken px-3 py-2 text-[15px] text-atx-ink placeholder:text-atx-ink-faint focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-atx-accent/60 disabled:cursor-not-allowed disabled:opacity-50"
        />
      </div>

      <div className="space-y-2">
        <Label className="text-[14px] font-medium text-atx-ink">Capabilities</Label>
        <div className="flex flex-wrap gap-2">
          {CAPABILITIES.map((cap) => {
            const isSelected = formState.capabilities.has(cap.id);
            return (
              <button
                key={cap.id}
                type="button"
                onClick={() => toggleCapability(cap.id)}
                className={cn(
                  "rounded-full border px-3.5 py-1.5 text-[14px] font-medium transition-colors duration-200",
                  isSelected
                    ? "border-atx-accent/50 bg-atx-accent/15 text-atx-accent"
                    : "border-atx-line text-atx-ink-mid hover:border-atx-ink-dim hover:text-atx-ink"
                )}
              >
                {cap.label}
              </button>
            );
          })}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="issuer-org" className="text-[14px] font-medium text-atx-ink">Issuer organization</Label>
        <Input
          id="issuer-org"
          placeholder="e.g., Acme Corp"
          value={formState.issuerOrg}
          onChange={(e) => onUpdate({ issuerOrg: e.target.value })}
          className="rounded-xl border-atx-line bg-atx-bg-sunken text-[15px] text-atx-ink placeholder:text-atx-ink-faint"
        />
      </div>

      <div className="space-y-2">
        <Label className="text-[14px] font-medium text-atx-ink">Risk level</Label>
        <div className="flex gap-3">
          {RISK_LEVELS.map((rl) => (
            <button
              key={rl.value}
              type="button"
              onClick={() => onUpdate({ riskLevel: rl.value })}
              className={cn(
                "flex-1 rounded-xl border px-4 py-3 text-center text-[14px] font-medium transition-colors duration-200",
                formState.riskLevel === rl.value
                  ? "border-atx-accent/50 bg-atx-accent/[0.05] text-atx-ink"
                  : "border-atx-line text-atx-ink-mid hover:border-atx-ink-dim"
              )}
            >
              <span className={cn(formState.riskLevel === rl.value && rl.color)}>
                {rl.label}
              </span>
            </button>
          ))}
        </div>
      </div>

      <button
        type="button"
        onClick={onSubmit}
        disabled={!canSubmit}
        className="inline-flex items-center justify-center gap-2 rounded-full bg-atx-accent px-6 py-3 text-[15px] font-medium text-[oklch(0.14_0.01_180)] transition-colors duration-200 hover:bg-atx-accent-deep w-full disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-atx-accent"
      >
        <Fingerprint className="h-4 w-4" />
        Create identity
      </button>
    </div>
  );
}

function IdentityCard({ identity }: { identity: AgentIdentity }) {
  const isVerified = identity.reputation_score > 0.7;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      {/* Tinted identity card */}
      <div className="rounded-2xl border border-atx-accent/30 bg-atx-accent/[0.05]">
        <div className="relative overflow-hidden rounded-2xl p-6 sm:p-8">
          {/* Watermark */}
          <div className="absolute top-4 right-4 sm:top-6 sm:right-6 opacity-[0.06] pointer-events-none select-none">
            <Shield className="h-24 w-24 sm:h-32 sm:w-32" />
          </div>

          {/* Header row */}
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-6">
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-[14px] font-medium text-atx-accent">
                <Shield className="h-3.5 w-3.5" />
                Attestix agent identity
              </div>
              <h2 className="text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink">
                {identity.display_name}
              </h2>
              {identity.description && (
                <p className="max-w-md text-[15px] leading-[1.6] text-atx-ink-mid">
                  {identity.description}
                </p>
              )}
            </div>

            <div className="flex items-center gap-3">
              {isVerified && (
                <motion.div
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.8, type: "spring", stiffness: 200 }}
                >
                  <span className="inline-flex items-center gap-1 rounded-full border border-atx-ok/30 bg-atx-ok/15 px-3 py-0.5 text-[13px] font-medium text-atx-ok">
                    <ShieldCheck className="h-3 w-3" />
                    Verified
                  </span>
                </motion.div>
              )}
              <div className="flex items-center gap-1.5">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-atx-ok opacity-75" />
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-atx-ok" />
                </span>
                <span className="text-[13px] font-medium text-atx-ok">Active</span>
              </div>
            </div>
          </div>

          {/* Main content grid */}
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_auto] gap-6">
            {/* Left column - details */}
            <div className="space-y-4">
              {/* Agent ID */}
              <div className="space-y-1">
                <span className="text-[13px] font-medium text-atx-ink-dim">
                  Agent ID
                </span>
                <div className="flex items-center">
                  <code className="rounded-lg bg-atx-bg-sunken px-2 py-1 font-mono-atx text-[13px] text-atx-ink">
                    {identity.agent_id}
                  </code>
                  <CopyButton text={identity.agent_id} />
                </div>
              </div>

              {/* DID */}
              <div className="space-y-1">
                <span className="text-[13px] font-medium text-atx-ink-dim">
                  Decentralized identifier (DID)
                </span>
                <div className="flex items-center">
                  <code className="rounded-lg bg-atx-bg-sunken px-2 py-1 font-mono-atx text-[13px] text-atx-ink break-all">
                    {identity.did.slice(0, 32)}...
                  </code>
                  <CopyButton text={identity.did} />
                </div>
              </div>

              {/* Issuer */}
              <div className="space-y-1">
                <span className="text-[13px] font-medium text-atx-ink-dim">
                  Issuer
                </span>
                <div className="flex items-center gap-2">
                  <UserCheck className="h-4 w-4 text-atx-accent" />
                  <span className="text-[15px] font-medium text-atx-ink">
                    {identity.issuer.name}
                  </span>
                  <code className="font-mono-atx text-[12px] text-atx-ink-dim">
                    ({identity.issuer.did.slice(0, 20)}...)
                  </code>
                </div>
              </div>

              {/* Capabilities */}
              <div className="space-y-1.5">
                <span className="text-[13px] font-medium text-atx-ink-dim">
                  Capabilities
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {identity.capabilities.map((cap) => {
                    const capInfo = CAPABILITIES.find((c) => c.id === cap);
                    return (
                      <span
                        key={cap}
                        className="rounded-full border border-atx-line bg-atx-panel/60 px-2.5 py-0.5 text-[13px] text-atx-ink-mid"
                      >
                        {capInfo?.label ?? cap}
                      </span>
                    );
                  })}
                </div>
              </div>

              {/* Risk Level + Created At row */}
              <div className="flex flex-wrap items-center gap-4">
                <div className="space-y-1">
                  <span className="text-[13px] font-medium text-atx-ink-dim">
                    Risk level
                  </span>
                  <div>
                    <RiskBadge level={identity.risk_level} />
                  </div>
                </div>
                <div className="space-y-1">
                  <span className="text-[13px] font-medium text-atx-ink-dim">
                    Created
                  </span>
                  <p className="text-[15px] text-atx-ink">
                    {new Date(identity.created_at).toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "short",
                      day: "numeric",
                    })}
                  </p>
                </div>
              </div>

              {/* Signature */}
              <div className="space-y-1">
                <span className="text-[13px] font-medium text-atx-ink-dim">
                  Signature
                </span>
                <div className="flex items-center">
                  <code className="rounded-lg bg-atx-bg-sunken px-2 py-1 font-mono-atx text-[12px] text-atx-ink-dim">
                    {identity.signature.slice(0, 32)}...
                  </code>
                  <CopyButton text={identity.signature} />
                </div>
              </div>
            </div>

            {/* Right column - trust score */}
            <div className="flex flex-col items-center justify-center lg:border-l lg:border-atx-line-soft lg:pl-6">
              <TrustScoreRing score={identity.reputation_score} />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function ExploreSection({ identity }: { identity: AgentIdentity }) {
  const jsonContent = JSON.stringify(
    {
      agent_id: identity.agent_id,
      display_name: identity.display_name,
      description: identity.description,
      issuer: identity.issuer,
      capabilities: identity.capabilities,
      created_at: identity.created_at,
      source_protocol: identity.source_protocol,
      risk_level: identity.risk_level,
      reputation_score: identity.reputation_score,
      signature: identity.signature,
      revoked: identity.revoked,
    },
    null,
    2
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3, duration: 0.5 }}
      className="mt-8 space-y-6"
    >
      <Accordion type="multiple" className="space-y-3">
        {/* What is this? */}
        <AccordionItem
          value="what-is-this"
          className="overflow-hidden rounded-2xl border border-atx-line bg-atx-panel/60 px-5"
        >
          <AccordionTrigger className="text-atx-ink transition-colors duration-200 hover:text-atx-accent hover:no-underline">
            <div className="flex items-center gap-2">
              <Key className="h-4 w-4 text-atx-accent" />
              <span className="text-[15px] font-medium">What is this?</span>
            </div>
          </AccordionTrigger>
          <AccordionContent className="text-atx-ink-mid">
            <div className="space-y-4">
              <FieldExplanation
                label="Agent ID"
                explanation="A unique identifier for your AI agent, like a passport number. It anchors the agent to the Attestix trust network and stays constant across interactions."
              />
              <FieldExplanation
                label="DID (Decentralized Identifier)"
                explanation="A self-sovereign identifier that works across any platform. Unlike a username controlled by a company, a DID is owned by the agent and can be verified anywhere without calling a central server."
              />
              <FieldExplanation
                label="Signature"
                explanation="Cryptographic proof that this identity was officially issued. If anyone tampers with any field, the signature becomes invalid, making forgery detectable."
              />
              <FieldExplanation
                label="Trust score"
                explanation="A reputation metric calculated from verified actions, credential checks, and peer interactions. It starts at 0.50 (neutral) and evolves over time as the agent builds a track record."
              />
              <FieldExplanation
                label="Capabilities"
                explanation="Declared abilities of the agent. Other systems can check these before delegating work, ensuring agents only perform tasks within their stated scope."
              />
              <FieldExplanation
                label="Risk level"
                explanation="Classification under the EU AI Act framework. Higher risk levels require more rigorous documentation, monitoring, and compliance measures."
              />
            </div>
          </AccordionContent>
        </AccordionItem>

        {/* Raw JSON */}
        <AccordionItem
          value="raw-json"
          className="overflow-hidden rounded-2xl border border-atx-line bg-atx-panel/60 px-5"
        >
          <AccordionTrigger className="text-atx-ink transition-colors duration-200 hover:text-atx-accent hover:no-underline">
            <div className="flex items-center gap-2">
              <FileCheck className="h-4 w-4 text-atx-accent" />
              <span className="text-[15px] font-medium">Raw JSON (UAIT structure)</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="relative">
              <div className="absolute top-2 right-2 z-10">
                <CopyButton text={jsonContent} />
              </div>
              <pre className="overflow-x-auto rounded-xl border border-atx-line-soft bg-atx-bg-sunken p-4 font-mono-atx text-[12px] leading-[1.7] text-atx-ink">
                {jsonContent}
              </pre>
            </div>
          </AccordionContent>
        </AccordionItem>

        {/* What can you do with this? */}
        <AccordionItem
          value="what-next"
          className="overflow-hidden rounded-2xl border border-atx-line bg-atx-panel/60 px-5"
        >
          <AccordionTrigger className="text-atx-ink transition-colors duration-200 hover:text-atx-accent hover:no-underline">
            <div className="flex items-center gap-2">
              <Star className="h-4 w-4 text-atx-accent" />
              <span className="text-[15px] font-medium">What can you do with this?</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <ActionCard
                icon={<Shield className="h-6 w-6" />}
                title="Prove identity"
                description="Present this identity to other agents or systems. They can verify the signature and trust score without calling Attestix directly."
              />
              <ActionCard
                icon={<Award className="h-6 w-6" />}
                title="Issue credentials"
                description="Attach verifiable claims to this agent, such as compliance certificates, audit results, or capability endorsements."
              />
              <ActionCard
                icon={<TrendingUp className="h-6 w-6" />}
                title="Build reputation"
                description="Earn trust through verified actions. Each successful interaction, credential check, and peer review contributes to the trust score."
              />
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      {/* CTA */}
      <div className="rounded-2xl border border-atx-accent/30 bg-atx-accent/[0.05] px-6 py-12 text-center">
        <h2 className="mb-3 text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink">
          Create real agent identities with Attestix
        </h2>
        <p className="mx-auto mb-8 max-w-[560px] text-[17.5px] leading-[1.6] text-atx-ink-mid">
          This was a simulation. With the Attestix MCP server, you can create
          cryptographically signed identities, anchor them on-chain, and build
          verifiable trust for your AI agents.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <Link href="/docs/getting-started" className="inline-flex items-center justify-center gap-2 rounded-full bg-atx-accent px-6 py-3 text-[15px] font-medium text-[oklch(0.14_0.01_180)] transition-colors duration-200 hover:bg-atx-accent-deep">
            Get started
            <ArrowRight className="h-4 w-4" />
          </Link>
          <Link
            href="/docs/examples#1-create-and-verify-an-agent-identity"
            className="inline-flex items-center justify-center gap-2 rounded-full border border-atx-line px-6 py-3 text-[15px] font-medium text-atx-ink-mid transition-colors duration-200 hover:border-atx-ink-dim hover:text-atx-ink"
          >
            <ExternalLink className="h-4 w-4" />
            View identity example
          </Link>
        </div>
      </div>
    </motion.div>
  );
}

function FieldExplanation({
  label,
  explanation,
}: {
  label: string;
  explanation: string;
}) {
  return (
    <div className="flex gap-3">
      <div className="mt-1 flex-shrink-0">
        <div className="mt-1 h-1.5 w-1.5 rounded-full bg-atx-accent" />
      </div>
      <div>
        <span className="text-[15px] font-medium text-atx-ink">{label}</span>
        <p className="mt-0.5 text-[14px] leading-[1.6] text-atx-ink-mid">{explanation}</p>
      </div>
    </div>
  );
}

function ActionCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="space-y-3 rounded-2xl border border-atx-line bg-atx-bg-sunken/70 p-5 transition-colors duration-200 hover:border-atx-ink-dim">
      <div className="text-atx-accent">{icon}</div>
      <h3 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">{title}</h3>
      <p className="text-[14px] leading-[1.55] text-atx-ink-mid">
        {description}
      </p>
    </div>
  );
}

// --- Main Component ---

export function IdentityExplorer() {
  const [step, setStep] = useState<"configure" | "result">("configure");
  const [formState, setFormState] = useState<AgentFormState>({
    name: "",
    description: "",
    capabilities: new Set<string>(),
    issuerOrg: "",
    riskLevel: "minimal",
  });
  const [identity, setIdentity] = useState<AgentIdentity | null>(null);

  const handleUpdate = useCallback(
    (updates: Partial<AgentFormState>) => {
      setFormState((prev) => ({ ...prev, ...updates }));
    },
    []
  );

  const handleSubmit = useCallback(() => {
    const generated = generateIdentity(formState);
    setIdentity(generated);
    setStep("result");
  }, [formState]);

  const handleStartOver = useCallback(() => {
    setStep("configure");
    setIdentity(null);
    setFormState({
      name: "",
      description: "",
      capabilities: new Set<string>(),
      issuerOrg: "",
      riskLevel: "minimal",
    });
  }, []);

  return (
    <div className="mx-auto w-full max-w-[960px] px-6">
      {/* Header */}
      <div className="pb-12 text-center">
        <p className="inline-flex items-center gap-2 text-[14px] font-medium text-atx-accent">
          <Fingerprint className="h-4 w-4" />
          <span>Agent identity explorer</span>
        </p>
        <h1 className="mt-3 text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
          What does an AI agent identity look like?
        </h1>
        <p className="mx-auto mt-5 max-w-[640px] text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
          Configure a simulated agent, generate its verifiable identity, and
          explore what each field means. Everything runs in your browser.
        </p>
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {step === "configure" && (
          <motion.div
            key="configure"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
          >
            <div className="rounded-2xl border border-atx-line bg-atx-panel/60 p-6 sm:p-8">
              <div className="flex items-center gap-2 mb-6">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-atx-accent text-[oklch(0.14_0.01_180)] text-[13px] font-medium">
                  1
                </div>
                <h2 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
                  Configure your agent
                </h2>
              </div>
              <ConfigurationForm
                formState={formState}
                onSubmit={handleSubmit}
                onUpdate={handleUpdate}
              />
            </div>
          </motion.div>
        )}

        {step === "result" && identity && (
          <motion.div
            key="result"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
          >
            <div className="space-y-6">
              {/* Back / Start Over */}
              <div className="flex items-center justify-between">
                <button type="button" onClick={handleStartOver} className="inline-flex items-center justify-center gap-2 rounded-full border border-atx-line px-6 py-3 text-[15px] font-medium text-atx-ink-mid transition-colors duration-200 hover:border-atx-ink-dim hover:text-atx-ink">
                  Create another
                </button>
                <div className="flex items-center gap-2 text-[14px] text-atx-ink-mid">
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-atx-accent text-[oklch(0.14_0.01_180)] text-[12px] font-medium">
                    2
                  </div>
                  Agent identity card
                </div>
              </div>

              {/* Identity Card */}
              <IdentityCard identity={identity} />

              {/* Explore Section */}
              <div className="flex items-center gap-2 mt-10 mb-2">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-atx-accent text-[oklch(0.14_0.01_180)] text-[12px] font-medium">
                  3
                </div>
                <h2 className="text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
                  Explore the identity
                </h2>
              </div>
              <ExploreSection identity={identity} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
