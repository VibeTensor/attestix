"use client";

import { useState, useCallback, useMemo } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "motion/react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  ArrowRight,
  Activity,
  Shield,
  Target,
  ShieldCheck,
  TrendingUp,
  TrendingDown,
  Minus,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  XCircle,
  Info,
} from "lucide-react";
import {
  AGENTS,
  generateTimeline,
  recalculateScore,
  getTrustLabel,
  getTrustColor,
  getTrustStroke,
  type AgentProfile,
} from "./data";

// ─────────────────────────────────────────────────
// Toast notification
// ─────────────────────────────────────────────────

interface Toast {
  id: number;
  message: string;
}

function ToastContainer({ toasts }: { toasts: Toast[] }) {
  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2">
      <AnimatePresence>
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.3 }}
            className="rounded-lg border border-border bg-card px-4 py-3 text-sm text-foreground shadow-lg max-w-sm"
          >
            {toast.message}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}

// ─────────────────────────────────────────────────
// Trend icon helper
// ─────────────────────────────────────────────────

function TrendIcon({ trend }: { trend: AgentProfile["trend"] }) {
  switch (trend) {
    case "improving":
    case "recovering":
      return <TrendingUp className="h-3.5 w-3.5 text-emerald-400" />;
    case "declining":
      return <TrendingDown className="h-3.5 w-3.5 text-red-400" />;
    case "stable":
      return <Minus className="h-3.5 w-3.5 text-blue-400" />;
  }
}

// ─────────────────────────────────────────────────
// Agent selector card
// ─────────────────────────────────────────────────

function AgentCard({
  agent,
  isSelected,
  onSelect,
}: {
  agent: AgentProfile;
  isSelected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      onClick={onSelect}
      className={cn(
        "flex-shrink-0 rounded-lg border p-4 text-left transition-all duration-200 min-w-[180px] cursor-pointer",
        isSelected
          ? "border-primary bg-primary/10 ring-1 ring-primary/30"
          : "border-border bg-card hover:border-primary/40 hover:bg-muted/50"
      )}
    >
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm font-semibold text-foreground truncate">
          {agent.name}
        </span>
        <TrendIcon trend={agent.trend} />
      </div>
      <p className="text-xs text-muted-foreground mb-2 truncate">{agent.role}</p>
      <span className={cn("text-2xl font-bold tabular-nums", getTrustColor(agent.trustScore))}>
        {agent.trustScore.toFixed(2)}
      </span>
    </button>
  );
}

// ─────────────────────────────────────────────────
// Circular trust score gauge (SVG)
// ─────────────────────────────────────────────────

function TrustGauge({
  score,
  totalInteractions,
}: {
  score: number;
  totalInteractions: number;
}) {
  const radius = 80;
  const strokeWidth = 10;
  const circumference = 2 * Math.PI * radius;
  const progress = score * circumference;
  const color = getTrustStroke(score);
  const label = getTrustLabel(score);

  return (
    <div className="flex flex-col items-center">
      <div className="relative">
        <svg width="200" height="200" viewBox="0 0 200 200">
          {/* Background circle */}
          <circle
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke="currentColor"
            className="text-muted/30"
            strokeWidth={strokeWidth}
          />
          {/* Progress arc */}
          <motion.circle
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: circumference - progress }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            transform="rotate(-90 100 100)"
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            key={score}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
            className={cn("text-4xl font-bold tabular-nums", getTrustColor(score))}
          >
            {score.toFixed(2)}
          </motion.span>
          <span className={cn("text-sm font-medium mt-1", getTrustColor(score))}>
            {label}
          </span>
        </div>
      </div>
      <p className="text-xs text-muted-foreground mt-3">
        Based on {totalInteractions} verified interactions
      </p>
    </div>
  );
}

// ─────────────────────────────────────────────────
// Category breakdown bars
// ─────────────────────────────────────────────────

interface CategoryBarProps {
  label: string;
  value: number;
  icon: React.ReactNode;
  delay: number;
}

function CategoryBar({ label, value, icon, delay }: CategoryBarProps) {
  const percentage = Math.round(value * 100);
  const color = getTrustStroke(value);

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm text-foreground">
          {icon}
          {label}
        </div>
        <span className="text-sm font-medium tabular-nums text-foreground">
          {percentage}%
        </span>
      </div>
      <div className="h-2.5 w-full rounded-full bg-muted/40">
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.6, ease: "easeOut", delay }}
        />
      </div>
    </div>
  );
}

function CategoryBreakdown({
  categories,
}: {
  categories: AgentProfile["categories"];
}) {
  return (
    <div className="space-y-5">
      <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
        <Activity className="h-4 w-4 text-muted-foreground" />
        Category Breakdown
      </h3>
      <div className="space-y-4">
        <CategoryBar
          label="Compliance"
          value={categories.compliance}
          icon={<Shield className="h-3.5 w-3.5 text-muted-foreground" />}
          delay={0}
        />
        <CategoryBar
          label="Accuracy"
          value={categories.accuracy}
          icon={<Target className="h-3.5 w-3.5 text-muted-foreground" />}
          delay={0.1}
        />
        <CategoryBar
          label="Safety"
          value={categories.safety}
          icon={<ShieldCheck className="h-3.5 w-3.5 text-muted-foreground" />}
          delay={0.2}
        />
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────
// Interaction donut chart (SVG)
// ─────────────────────────────────────────────────

function InteractionDonut({
  interactions,
}: {
  interactions: AgentProfile["interactions"];
}) {
  const { total, success, partial, failure } = interactions;
  const radius = 50;
  const strokeWidth = 14;
  const circumference = 2 * Math.PI * radius;

  const successPct = success / total;
  const partialPct = partial / total;
  const failurePct = failure / total;

  const successLen = successPct * circumference;
  const partialLen = partialPct * circumference;
  const failureLen = failurePct * circumference;

  const successOffset = 0;
  const partialOffset = successLen;
  const failureOffset = successLen + partialLen;

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
        <Activity className="h-4 w-4 text-muted-foreground" />
        Interaction History
      </h3>
      <div className="flex items-center gap-6">
        <svg width="130" height="130" viewBox="0 0 130 130">
          {/* Success arc */}
          <circle
            cx="65"
            cy="65"
            r={radius}
            fill="none"
            stroke="#34d399"
            strokeWidth={strokeWidth}
            strokeDasharray={`${successLen} ${circumference - successLen}`}
            strokeDashoffset={-successOffset}
            transform="rotate(-90 65 65)"
          />
          {/* Partial arc */}
          <circle
            cx="65"
            cy="65"
            r={radius}
            fill="none"
            stroke="#facc15"
            strokeWidth={strokeWidth}
            strokeDasharray={`${partialLen} ${circumference - partialLen}`}
            strokeDashoffset={-partialOffset}
            transform="rotate(-90 65 65)"
          />
          {/* Failure arc */}
          <circle
            cx="65"
            cy="65"
            r={radius}
            fill="none"
            stroke="#f87171"
            strokeWidth={strokeWidth}
            strokeDasharray={`${failureLen} ${circumference - failureLen}`}
            strokeDashoffset={-failureOffset}
            transform="rotate(-90 65 65)"
          />
          {/* Center text */}
          <text
            x="65"
            y="62"
            textAnchor="middle"
            className="fill-foreground text-xl font-bold"
            dominantBaseline="central"
          >
            {total}
          </text>
          <text
            x="65"
            y="80"
            textAnchor="middle"
            className="fill-muted-foreground text-[10px]"
          >
            total
          </text>
        </svg>
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2">
            <span className="inline-block h-3 w-3 rounded-full bg-emerald-400" />
            <span className="text-muted-foreground">Success</span>
            <span className="font-medium text-foreground ml-auto tabular-nums">{success}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block h-3 w-3 rounded-full bg-yellow-400" />
            <span className="text-muted-foreground">Partial</span>
            <span className="font-medium text-foreground ml-auto tabular-nums">{partial}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block h-3 w-3 rounded-full bg-red-400" />
            <span className="text-muted-foreground">Failure</span>
            <span className="font-medium text-foreground ml-auto tabular-nums">{failure}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────
// Timeline chart (SVG path)
// ─────────────────────────────────────────────────

function TimelineChart({
  agentId,
  timeline,
  currentScore,
}: {
  agentId: string;
  timeline: { day: number; score: number }[];
  currentScore: number;
}) {
  const chartWidth = 800;
  const chartHeight = 200;
  const paddingX = 40;
  const paddingTop = 10;
  const paddingBottom = 30;

  const plotWidth = chartWidth - paddingX * 2;
  const plotHeight = chartHeight - paddingTop - paddingBottom;

  const points = timeline.map((p, i) => {
    const x = paddingX + (i / (timeline.length - 1)) * plotWidth;
    const y = paddingTop + plotHeight - p.score * plotHeight;
    return { x, y };
  });

  const pathD = points
    .map((p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `L ${p.x} ${p.y}`))
    .join(" ");

  // Area fill path
  const areaD = `${pathD} L ${points[points.length - 1].x} ${paddingTop + plotHeight} L ${points[0].x} ${paddingTop + plotHeight} Z`;

  const strokeColor = getTrustStroke(currentScore);

  // Y-axis labels
  const yLabels = [0, 0.25, 0.5, 0.75, 1.0];

  // X-axis labels (every 30 days)
  const xLabels = [0, 30, 60, 89];

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
        <TrendingUp className="h-4 w-4 text-muted-foreground" />
        Trust Score Timeline (90 days)
      </h3>
      <div className="w-full overflow-x-auto">
        <svg
          viewBox={`0 0 ${chartWidth} ${chartHeight}`}
          className="w-full min-w-[500px]"
          preserveAspectRatio="xMidYMid meet"
        >
          {/* Grid lines */}
          {yLabels.map((val) => {
            const y = paddingTop + plotHeight - val * plotHeight;
            return (
              <g key={val}>
                <line
                  x1={paddingX}
                  y1={y}
                  x2={paddingX + plotWidth}
                  y2={y}
                  stroke="currentColor"
                  className="text-muted/20"
                  strokeDasharray="4 4"
                />
                <text
                  x={paddingX - 6}
                  y={y + 4}
                  textAnchor="end"
                  className="fill-muted-foreground text-[10px]"
                >
                  {val.toFixed(1)}
                </text>
              </g>
            );
          })}

          {/* X-axis labels */}
          {xLabels.map((day) => {
            const x = paddingX + (day / 89) * plotWidth;
            return (
              <text
                key={day}
                x={x}
                y={chartHeight - 5}
                textAnchor="middle"
                className="fill-muted-foreground text-[10px]"
              >
                {day === 0 ? "90d ago" : day === 89 ? "Today" : `${90 - day}d ago`}
              </text>
            );
          })}

          {/* Threshold lines */}
          {/* 0.7 threshold */}
          <line
            x1={paddingX}
            y1={paddingTop + plotHeight - 0.7 * plotHeight}
            x2={paddingX + plotWidth}
            y2={paddingTop + plotHeight - 0.7 * plotHeight}
            stroke="#34d399"
            strokeWidth={0.5}
            strokeDasharray="6 3"
            opacity={0.4}
          />
          {/* 0.5 threshold */}
          <line
            x1={paddingX}
            y1={paddingTop + plotHeight - 0.5 * plotHeight}
            x2={paddingX + plotWidth}
            y2={paddingTop + plotHeight - 0.5 * plotHeight}
            stroke="#facc15"
            strokeWidth={0.5}
            strokeDasharray="6 3"
            opacity={0.4}
          />

          {/* Area fill */}
          <motion.path
            key={`area-${agentId}`}
            d={areaD}
            fill={strokeColor}
            opacity={0.08}
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.08 }}
            transition={{ duration: 0.6 }}
          />

          {/* Line path */}
          <motion.path
            key={`line-${agentId}`}
            d={pathD}
            fill="none"
            stroke={strokeColor}
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1, ease: "easeOut" }}
          />

          {/* Current score dot */}
          <motion.circle
            key={`dot-${agentId}`}
            cx={points[points.length - 1].x}
            cy={points[points.length - 1].y}
            r={4}
            fill={strokeColor}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: 0.8 }}
          />
        </svg>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────
// Simulate interaction buttons
// ─────────────────────────────────────────────────

function SimulateControls({
  onSimulate,
}: {
  onSimulate: (outcome: "success" | "partial" | "failure") => void;
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-6">
      <h3 className="text-sm font-semibold text-foreground mb-1">
        Simulate an Event
      </h3>
      <p className="text-xs text-muted-foreground mb-4">
        Record a simulated interaction and watch the trust score update in real time.
      </p>
      <div className="flex flex-wrap gap-3">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onSimulate("success")}
          className="border-emerald-500/30 hover:bg-emerald-500/10 hover:text-emerald-400 hover:border-emerald-500/50"
        >
          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          Record Success
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onSimulate("partial")}
          className="border-yellow-500/30 hover:bg-yellow-500/10 hover:text-yellow-400 hover:border-yellow-500/50"
        >
          <AlertCircle className="h-4 w-4 text-yellow-400" />
          Record Partial
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onSimulate("failure")}
          className="border-red-500/30 hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/50"
        >
          <XCircle className="h-4 w-4 text-red-400" />
          Record Failure
        </Button>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────
// Explainer section
// ─────────────────────────────────────────────────

function Explainer() {
  const items = [
    "Trust scores update dynamically based on verified behavior, compliance events, and peer attestations.",
    "A score above 0.7 indicates a reliable agent with strong compliance history.",
    "Scores use exponential decay with a 30-day half-life - recent behavior matters more.",
  ];

  return (
    <div className="rounded-lg border border-border bg-card p-6">
      <h3 className="text-sm font-semibold text-foreground flex items-center gap-2 mb-3">
        <Info className="h-4 w-4 text-muted-foreground" />
        What does this mean?
      </h3>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
            <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary flex-shrink-0" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

// ─────────────────────────────────────────────────
// Main dashboard component
// ─────────────────────────────────────────────────

export function ReputationDashboard() {
  const [selectedId, setSelectedId] = useState(AGENTS[0].id);
  const [scoreOverrides, setScoreOverrides] = useState<Record<string, number>>({});
  const [interactionOverrides, setInteractionOverrides] = useState<
    Record<string, AgentProfile["interactions"]>
  >({});
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [toastCounter, setToastCounter] = useState(0);

  const selectedAgent = AGENTS.find((a) => a.id === selectedId)!;
  const currentScore = scoreOverrides[selectedId] ?? selectedAgent.trustScore;
  const currentInteractions =
    interactionOverrides[selectedId] ?? selectedAgent.interactions;

  const timeline = useMemo(
    () => generateTimeline(selectedAgent),
    [selectedAgent]
  );

  // Build a modified timeline that ends at the current (possibly overridden) score
  const adjustedTimeline = useMemo(() => {
    if (currentScore === selectedAgent.trustScore) return timeline;
    const diff = currentScore - selectedAgent.trustScore;
    // Only adjust the last ~10 points to show recent change
    return timeline.map((p, i) => {
      if (i >= 80) {
        const factor = (i - 80) / 9;
        return { day: p.day, score: Math.max(0, Math.min(1, p.score + diff * factor)) };
      }
      return p;
    });
  }, [timeline, currentScore, selectedAgent.trustScore]);

  const addToast = useCallback(
    (message: string) => {
      const id = toastCounter + 1;
      setToastCounter(id);
      setToasts((prev) => [...prev, { id, message }]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, 3000);
    },
    [toastCounter]
  );

  const handleSimulate = useCallback(
    (outcome: "success" | "partial" | "failure") => {
      const oldScore = currentScore;
      const newScore = recalculateScore(oldScore, outcome);
      setScoreOverrides((prev) => ({ ...prev, [selectedId]: newScore }));

      // Update interactions
      const prev = currentInteractions;
      const updated = {
        total: prev.total + 1,
        success: prev.success + (outcome === "success" ? 1 : 0),
        partial: prev.partial + (outcome === "partial" ? 1 : 0),
        failure: prev.failure + (outcome === "failure" ? 1 : 0),
      };
      setInteractionOverrides((prevMap) => ({
        ...prevMap,
        [selectedId]: updated,
      }));

      addToast(
        `Interaction recorded. Trust score updated: ${oldScore.toFixed(2)} -> ${newScore.toFixed(2)}`
      );
    },
    [currentScore, currentInteractions, selectedId, addToast]
  );

  const handleReset = useCallback(() => {
    setScoreOverrides((prev) => {
      const next = { ...prev };
      delete next[selectedId];
      return next;
    });
    setInteractionOverrides((prev) => {
      const next = { ...prev };
      delete next[selectedId];
      return next;
    });
    addToast("Agent data reset to original values.");
  }, [selectedId, addToast]);

  const hasOverride =
    selectedId in scoreOverrides || selectedId in interactionOverrides;

  return (
    <div className="mx-auto max-w-6xl px-4 sm:px-6">
      {/* Header */}
      <div className="text-center py-12">
        <div className="inline-flex items-center gap-2 rounded-full border border-border bg-muted/50 px-4 py-1.5 text-sm text-muted-foreground mb-6">
          <Shield className="h-4 w-4" />
          <span>AI Agent Reputation Dashboard</span>
        </div>
        <h1 className="text-3xl font-bold text-foreground sm:text-4xl lg:text-5xl tracking-tight">
          Verifiable reputation for AI agents
        </h1>
        <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
          Trust scores update dynamically based on verified behavior. Select an
          agent below to explore its reputation profile, or simulate new
          interactions to see scores change in real time.
        </p>
      </div>

      {/* Agent Selector */}
      <div className="mb-8">
        <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin">
          {AGENTS.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={{
                ...agent,
                trustScore: scoreOverrides[agent.id] ?? agent.trustScore,
              }}
              isSelected={agent.id === selectedId}
              onSelect={() => setSelectedId(agent.id)}
            />
          ))}
        </div>
      </div>

      {/* Main Dashboard Grid */}
      <AnimatePresence mode="wait">
        <motion.div
          key={selectedId}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.3 }}
        >
          {/* Agent name and reset */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-semibold text-foreground">
                {selectedAgent.name}
              </h2>
              <p className="text-sm text-muted-foreground">
                {selectedAgent.role}
              </p>
            </div>
            {hasOverride && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleReset}
                className="text-muted-foreground"
              >
                <RotateCcw className="h-3.5 w-3.5" />
                Reset
              </Button>
            )}
          </div>

          {/* Three column layout */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Column 1: Trust Score */}
            <div className="rounded-lg border border-border bg-card p-6 flex items-center justify-center">
              <TrustGauge
                score={currentScore}
                totalInteractions={currentInteractions.total}
              />
            </div>

            {/* Column 2: Category Breakdown */}
            <div className="rounded-lg border border-border bg-card p-6">
              <CategoryBreakdown categories={selectedAgent.categories} />
            </div>

            {/* Column 3: Interaction History */}
            <div className="rounded-lg border border-border bg-card p-6">
              <InteractionDonut interactions={currentInteractions} />
            </div>
          </div>

          {/* Timeline chart */}
          <div className="rounded-lg border border-border bg-card p-6 mb-6">
            <TimelineChart
              agentId={selectedId}
              timeline={adjustedTimeline}
              currentScore={currentScore}
            />
          </div>

          {/* Explainer + Simulate side by side */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
            <Explainer />
            <SimulateControls onSimulate={handleSimulate} />
          </div>
        </motion.div>
      </AnimatePresence>

      {/* CTA section */}
      <div className="rounded-xl border border-primary/20 bg-primary/5 p-8 text-center">
        <h2 className="text-2xl font-bold text-foreground mb-3">
          Build real reputation tracking for your AI agents
        </h2>
        <p className="text-muted-foreground mb-6 max-w-xl mx-auto">
          Attestix provides cryptographically verifiable reputation scores,
          interaction logging, and trust attestations for any AI agent. Start
          building trust infrastructure in minutes.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <Link href="/docs/getting-started">
            <Button size="lg">
              Get started
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/docs/guides/reputation">
            <Button variant="outline" size="lg">
              Reputation guide
            </Button>
          </Link>
        </div>
      </div>

      {/* Toast notifications */}
      <ToastContainer toasts={toasts} />
    </div>
  );
}
