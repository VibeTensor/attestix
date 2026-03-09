"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import { AnimatePresence, motion, useSpring, useMotionValue } from "motion/react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
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
  { value: "minimal", label: "Minimal", color: "text-emerald-400" },
  { value: "limited", label: "Limited", color: "text-yellow-400" },
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
          className="text-muted/30"
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
        <span className="text-2xl font-bold text-foreground tabular-nums">
          {displayValue.toFixed(2)}
        </span>
        <span className="text-xs text-muted-foreground">Trust Score</span>
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
      className="ml-2 inline-flex items-center text-muted-foreground hover:text-foreground transition-colors"
      title="Copy to clipboard"
      type="button"
    >
      {copied ? (
        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
      ) : (
        <Copy className="h-3.5 w-3.5" />
      )}
    </button>
  );
}

function RiskBadge({ level }: { level: RiskLevel }) {
  const config = {
    minimal: {
      label: "Minimal Risk",
      className: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    },
    limited: {
      label: "Limited Risk",
      className: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
    },
    high: {
      label: "High Risk",
      className: "bg-orange-500/15 text-orange-400 border-orange-500/30",
    },
  };

  const { label, className } = config[level];

  return (
    <Badge variant="outline" className={className}>
      {label}
    </Badge>
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
        <Label htmlFor="agent-name">Agent Name</Label>
        <Input
          id="agent-name"
          placeholder="e.g., Data Analysis Bot"
          value={formState.name}
          onChange={(e) => onUpdate({ name: e.target.value })}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="agent-description">Description</Label>
        <textarea
          id="agent-description"
          placeholder="e.g., Analyzes quarterly financial data"
          value={formState.description}
          onChange={(e) => onUpdate({ description: e.target.value })}
          rows={3}
          className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
        />
      </div>

      <div className="space-y-2">
        <Label>Capabilities</Label>
        <div className="flex flex-wrap gap-2">
          {CAPABILITIES.map((cap) => {
            const isSelected = formState.capabilities.has(cap.id);
            return (
              <button
                key={cap.id}
                type="button"
                onClick={() => toggleCapability(cap.id)}
                className={cn(
                  "rounded-full border px-3 py-1.5 text-sm font-medium transition-all",
                  isSelected
                    ? "border-primary bg-primary/15 text-primary"
                    : "border-border bg-muted/30 text-muted-foreground hover:border-primary/40 hover:text-foreground"
                )}
              >
                {cap.label}
              </button>
            );
          })}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="issuer-org">Issuer Organization</Label>
        <Input
          id="issuer-org"
          placeholder="e.g., Acme Corp"
          value={formState.issuerOrg}
          onChange={(e) => onUpdate({ issuerOrg: e.target.value })}
        />
      </div>

      <div className="space-y-2">
        <Label>Risk Level</Label>
        <div className="flex gap-3">
          {RISK_LEVELS.map((rl) => (
            <button
              key={rl.value}
              type="button"
              onClick={() => onUpdate({ riskLevel: rl.value })}
              className={cn(
                "flex-1 rounded-lg border px-4 py-3 text-sm font-medium transition-all text-center",
                formState.riskLevel === rl.value
                  ? "border-primary bg-primary/10 text-foreground"
                  : "border-border bg-muted/30 text-muted-foreground hover:border-primary/40"
              )}
            >
              <span className={cn(formState.riskLevel === rl.value && rl.color)}>
                {rl.label}
              </span>
            </button>
          ))}
        </div>
      </div>

      <Button
        onClick={onSubmit}
        disabled={!canSubmit}
        size="lg"
        className="w-full"
      >
        <Fingerprint className="h-4 w-4" />
        Create Identity
      </Button>
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
      {/* Card with gradient border */}
      <div className="rounded-2xl p-[1px] bg-gradient-to-br from-indigo-500 via-indigo-400/50 to-amber-500/80">
        <div className="rounded-2xl bg-card/95 backdrop-blur-sm p-6 sm:p-8 relative overflow-hidden">
          {/* Watermark */}
          <div className="absolute top-4 right-4 sm:top-6 sm:right-6 opacity-[0.06] pointer-events-none select-none">
            <Shield className="h-24 w-24 sm:h-32 sm:w-32" />
          </div>

          {/* Header row */}
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-6">
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-xs text-muted-foreground uppercase tracking-wider font-medium">
                <Shield className="h-3.5 w-3.5 text-primary" />
                Attestix Agent Identity
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold text-foreground">
                {identity.display_name}
              </h2>
              {identity.description && (
                <p className="text-sm text-muted-foreground max-w-md">
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
                  <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30 gap-1">
                    <ShieldCheck className="h-3 w-3" />
                    Verified
                  </Badge>
                </motion.div>
              )}
              <div className="flex items-center gap-1.5">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
                </span>
                <span className="text-xs font-medium text-emerald-400">Active</span>
              </div>
            </div>
          </div>

          {/* Main content grid */}
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_auto] gap-6">
            {/* Left column - details */}
            <div className="space-y-4">
              {/* Agent ID */}
              <div className="space-y-1">
                <span className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
                  Agent ID
                </span>
                <div className="flex items-center">
                  <code className="text-sm font-mono text-foreground bg-muted/30 rounded px-2 py-1">
                    {identity.agent_id}
                  </code>
                  <CopyButton text={identity.agent_id} />
                </div>
              </div>

              {/* DID */}
              <div className="space-y-1">
                <span className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
                  Decentralized Identifier (DID)
                </span>
                <div className="flex items-center">
                  <code className="text-sm font-mono text-foreground bg-muted/30 rounded px-2 py-1 break-all">
                    {identity.did.slice(0, 32)}...
                  </code>
                  <CopyButton text={identity.did} />
                </div>
              </div>

              {/* Issuer */}
              <div className="space-y-1">
                <span className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
                  Issuer
                </span>
                <div className="flex items-center gap-2">
                  <UserCheck className="h-4 w-4 text-primary" />
                  <span className="text-sm text-foreground font-medium">
                    {identity.issuer.name}
                  </span>
                  <code className="text-xs font-mono text-muted-foreground">
                    ({identity.issuer.did.slice(0, 20)}...)
                  </code>
                </div>
              </div>

              {/* Capabilities */}
              <div className="space-y-1.5">
                <span className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
                  Capabilities
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {identity.capabilities.map((cap) => {
                    const capInfo = CAPABILITIES.find((c) => c.id === cap);
                    return (
                      <Badge
                        key={cap}
                        variant="secondary"
                        className="text-xs"
                      >
                        {capInfo?.label ?? cap}
                      </Badge>
                    );
                  })}
                </div>
              </div>

              {/* Risk Level + Created At row */}
              <div className="flex flex-wrap items-center gap-4">
                <div className="space-y-1">
                  <span className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
                    Risk Level
                  </span>
                  <div>
                    <RiskBadge level={identity.risk_level} />
                  </div>
                </div>
                <div className="space-y-1">
                  <span className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
                    Created
                  </span>
                  <p className="text-sm text-foreground font-mono">
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
                <span className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
                  Signature
                </span>
                <div className="flex items-center">
                  <code className="text-xs font-mono text-muted-foreground bg-muted/20 rounded px-2 py-1">
                    {identity.signature.slice(0, 32)}...
                  </code>
                  <CopyButton text={identity.signature} />
                </div>
              </div>
            </div>

            {/* Right column - trust score */}
            <div className="flex flex-col items-center justify-center lg:border-l lg:border-border/50 lg:pl-6">
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
          className="rounded-lg border border-border bg-card/50 px-4 overflow-hidden"
        >
          <AccordionTrigger className="hover:no-underline text-foreground">
            <div className="flex items-center gap-2">
              <Key className="h-4 w-4 text-primary" />
              <span className="font-semibold">What is this?</span>
            </div>
          </AccordionTrigger>
          <AccordionContent className="text-muted-foreground">
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
                label="Trust Score"
                explanation="A reputation metric calculated from verified actions, credential checks, and peer interactions. It starts at 0.50 (neutral) and evolves over time as the agent builds a track record."
              />
              <FieldExplanation
                label="Capabilities"
                explanation="Declared abilities of the agent. Other systems can check these before delegating work, ensuring agents only perform tasks within their stated scope."
              />
              <FieldExplanation
                label="Risk Level"
                explanation="Classification under the EU AI Act framework. Higher risk levels require more rigorous documentation, monitoring, and compliance measures."
              />
            </div>
          </AccordionContent>
        </AccordionItem>

        {/* Raw JSON */}
        <AccordionItem
          value="raw-json"
          className="rounded-lg border border-border bg-card/50 px-4 overflow-hidden"
        >
          <AccordionTrigger className="hover:no-underline text-foreground">
            <div className="flex items-center gap-2">
              <FileCheck className="h-4 w-4 text-primary" />
              <span className="font-semibold">Raw JSON (UAIT Structure)</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="relative">
              <div className="absolute top-2 right-2 z-10">
                <CopyButton text={jsonContent} />
              </div>
              <pre className="rounded-lg bg-muted/30 border border-border p-4 text-xs font-mono text-foreground overflow-x-auto leading-relaxed">
                {jsonContent}
              </pre>
            </div>
          </AccordionContent>
        </AccordionItem>

        {/* What can you do with this? */}
        <AccordionItem
          value="what-next"
          className="rounded-lg border border-border bg-card/50 px-4 overflow-hidden"
        >
          <AccordionTrigger className="hover:no-underline text-foreground">
            <div className="flex items-center gap-2">
              <Star className="h-4 w-4 text-primary" />
              <span className="font-semibold">What can you do with this?</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <ActionCard
                icon={<Shield className="h-6 w-6" />}
                title="Prove Identity"
                description="Present this identity to other agents or systems. They can verify the signature and trust score without calling Attestix directly."
              />
              <ActionCard
                icon={<Award className="h-6 w-6" />}
                title="Issue Credentials"
                description="Attach verifiable claims to this agent, such as compliance certificates, audit results, or capability endorsements."
              />
              <ActionCard
                icon={<TrendingUp className="h-6 w-6" />}
                title="Build Reputation"
                description="Earn trust through verified actions. Each successful interaction, credential check, and peer review contributes to the trust score."
              />
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      {/* CTA */}
      <div className="rounded-xl border border-primary/20 bg-primary/5 p-8 text-center">
        <h2 className="text-2xl font-bold text-foreground mb-3">
          Create real agent identities with Attestix
        </h2>
        <p className="text-muted-foreground mb-6 max-w-xl mx-auto">
          This was a simulation. With the Attestix MCP server, you can create
          cryptographically signed identities, anchor them on-chain, and build
          verifiable trust for your AI agents.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <Link href="/docs/getting-started">
            <Button size="lg">
              Get started
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/docs/examples#1-create-and-verify-an-agent-identity">
            <Button variant="outline" size="lg">
              <ExternalLink className="h-4 w-4" />
              View identity example
            </Button>
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
        <div className="h-1.5 w-1.5 rounded-full bg-primary" />
      </div>
      <div>
        <span className="text-sm font-medium text-foreground">{label}</span>
        <p className="text-sm text-muted-foreground mt-0.5">{explanation}</p>
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
    <div className="rounded-lg border border-border bg-card p-5 space-y-3">
      <div className="text-primary">{icon}</div>
      <h3 className="font-semibold text-foreground">{title}</h3>
      <p className="text-sm text-muted-foreground leading-relaxed">
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
    <div className="mx-auto max-w-4xl px-4 sm:px-6">
      {/* Header */}
      <div className="text-center py-12">
        <div className="inline-flex items-center gap-2 rounded-full border border-border bg-muted/50 px-4 py-1.5 text-sm text-muted-foreground mb-6">
          <Fingerprint className="h-4 w-4" />
          <span>Agent Identity Explorer</span>
        </div>
        <h1 className="text-3xl font-bold text-foreground sm:text-4xl lg:text-5xl tracking-tight">
          What does an AI agent identity look like?
        </h1>
        <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
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
            <div className="rounded-xl border border-border bg-card p-6 sm:p-8">
              <div className="flex items-center gap-2 mb-6">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
                  1
                </div>
                <h2 className="text-lg font-semibold text-foreground">
                  Configure Your Agent
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
                <Button variant="outline" onClick={handleStartOver}>
                  Create Another
                </Button>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs font-medium">
                    2
                  </div>
                  Agent Identity Card
                </div>
              </div>

              {/* Identity Card */}
              <IdentityCard identity={identity} />

              {/* Explore Section */}
              <div className="flex items-center gap-2 mt-10 mb-2">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs font-medium">
                  3
                </div>
                <h2 className="text-lg font-semibold text-foreground">
                  Explore the Identity
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
