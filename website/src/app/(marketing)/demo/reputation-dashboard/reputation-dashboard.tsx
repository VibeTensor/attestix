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
            className="max-w-sm rounded-xl border border-atx-line bg-atx-panel px-4 py-3 text-[14px] text-atx-ink shadow-lg"
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
        "min-w-[180px] flex-shrink-0 cursor-pointer rounded-2xl border p-4 text-left transition-colors duration-200",
        isSelected
          ? "border-atx-accent/50 bg-atx-accent/[0.05]"
          : "border-atx-line bg-atx-panel/60 hover:border-atx-ink-dim"
      )}
    >
      <div className="flex items-center justify-between mb-1">
        <span className="truncate text-[15px] font-semibold tracking-[-0.2px] text-atx-ink">
          {agent.name}
        </span>
        <TrendIcon trend={agent.trend} />
      </div>
      <p className="mb-2 truncate text-[13px] text-atx-ink-dim">{agent.role}</p>
      <span className={cn("font-mono-atx text-[24px] font-medium tabular-nums", getTrustColor(agent.trustScore))}>
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
            className="text-atx-line-soft"
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
            className={cn("font-mono-atx text-[36px] font-medium tabular-nums", getTrustColor(score))}
          >
            {score.toFixed(2)}
          </motion.span>
          <span className={cn("text-sm font-medium mt-1", getTrustColor(score))}>
            {label}
          </span>
        </div>
      </div>
      <p className="mt-3 text-[13px] text-atx-ink-dim">
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
        <div className="flex items-center gap-2 text-[14px] text-atx-ink-mid">
          {icon}
          {label}
        </div>
        <span className="font-mono-atx text-[13px] tabular-nums text-atx-ink">
          {percentage}%
        </span>
      </div>
      <div className="h-2.5 w-full rounded-full bg-atx-bg-sunken">
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
      <h3 className="flex items-center gap-2 text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
        <Activity className="h-4 w-4 text-atx-ink-dim" />
        Category breakdown
      </h3>
      <div className="space-y-4">
        <CategoryBar
          label="Compliance"
          value={categories.compliance}
          icon={<Shield className="h-3.5 w-3.5 text-atx-ink-dim" />}
          delay={0}
        />
        <CategoryBar
          label="Accuracy"
          value={categories.accuracy}
          icon={<Target className="h-3.5 w-3.5 text-atx-ink-dim" />}
          delay={0.1}
        />
        <CategoryBar
          label="Safety"
          value={categories.safety}
          icon={<ShieldCheck className="h-3.5 w-3.5 text-atx-ink-dim" />}
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
      <h3 className="flex items-center gap-2 text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
        <Activity className="h-4 w-4 text-atx-ink-dim" />
        Interaction history
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
            className="fill-atx-ink font-mono-atx text-xl font-medium"
            dominantBaseline="central"
          >
            {total}
          </text>
          <text
            x="65"
            y="80"
            textAnchor="middle"
            className="fill-atx-ink-dim text-[10px]"
          >
            total
          </text>
        </svg>
        <div className="space-y-2 text-[14px]">
          <div className="flex items-center gap-2">
            <span className="inline-block h-3 w-3 rounded-full bg-emerald-400" />
            <span className="text-atx-ink-mid">Success</span>
            <span className="ml-auto font-mono-atx text-[13px] tabular-nums text-atx-ink">{success}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block h-3 w-3 rounded-full bg-yellow-400" />
            <span className="text-atx-ink-mid">Partial</span>
            <span className="ml-auto font-mono-atx text-[13px] tabular-nums text-atx-ink">{partial}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block h-3 w-3 rounded-full bg-red-400" />
            <span className="text-atx-ink-mid">Failure</span>
            <span className="ml-auto font-mono-atx text-[13px] tabular-nums text-atx-ink">{failure}</span>
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
      <h3 className="flex items-center gap-2 text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
        <TrendingUp className="h-4 w-4 text-atx-ink-dim" />
        Trust score timeline (90 days)
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
                  className="text-atx-line-soft"
                  strokeDasharray="4 4"
                />
                <text
                  x={paddingX - 6}
                  y={y + 4}
                  textAnchor="end"
                  className="fill-atx-ink-dim text-[10px]"
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
                className="fill-atx-ink-dim text-[10px]"
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
    <div className="rounded-2xl border border-atx-line bg-atx-panel/60 p-6">
      <h3 className="mb-1 text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
        Simulate an event
      </h3>
      <p className="mb-4 text-[14px] leading-[1.55] text-atx-ink-mid">
        Record a simulated interaction and watch the trust score update in real time.
      </p>
      <div className="flex flex-wrap gap-3">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onSimulate("success")}
          className="rounded-full bg-transparent transition-colors duration-200 border-emerald-500/30 hover:bg-emerald-500/10 hover:text-emerald-400 hover:border-emerald-500/50"
        >
          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          Record success
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onSimulate("partial")}
          className="rounded-full bg-transparent transition-colors duration-200 border-yellow-500/30 hover:bg-yellow-500/10 hover:text-yellow-400 hover:border-yellow-500/50"
        >
          <AlertCircle className="h-4 w-4 text-yellow-400" />
          Record partial
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onSimulate("failure")}
          className="rounded-full bg-transparent transition-colors duration-200 border-red-500/30 hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/50"
        >
          <XCircle className="h-4 w-4 text-red-400" />
          Record failure
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
    <div className="rounded-2xl border border-atx-line bg-atx-panel/60 p-6">
      <h3 className="mb-3 flex items-center gap-2 text-[19px] font-semibold tracking-[-0.48px] text-atx-ink">
        <Info className="h-4 w-4 text-atx-ink-dim" />
        What does this mean?
      </h3>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <li key={i} className="flex items-start gap-2 text-[14px] leading-[1.55] text-atx-ink-mid">
            <span className="mt-2 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-atx-accent" />
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
    <div className="mx-auto w-full max-w-[1200px] px-6">
      {/* Header */}
      <div className="pb-12 pt-16 text-center">
        <p className="text-[14px] font-medium text-atx-accent">
          AI agent reputation dashboard
        </p>
        <h1 className="mx-auto mt-3 max-w-[860px] text-[clamp(34px,5vw,52px)] font-normal leading-[1.09] tracking-[-0.03em] text-atx-ink [text-wrap:balance]">
          Verifiable reputation for AI agents
        </h1>
        <p className="mx-auto mt-5 max-w-[640px] text-[17.5px] leading-[1.6] text-atx-ink-mid [text-wrap:balance]">
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
              <h2 className="text-[24px] font-medium tracking-[-0.5px] text-atx-ink">
                {selectedAgent.name}
              </h2>
              <p className="text-[14px] text-atx-ink-dim">
                {selectedAgent.role}
              </p>
            </div>
            {hasOverride && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleReset}
                className="rounded-full border-atx-line bg-transparent text-atx-ink-mid transition-colors duration-200 hover:border-atx-ink-dim hover:bg-transparent hover:text-atx-ink"
              >
                <RotateCcw className="h-3.5 w-3.5" />
                Reset
              </Button>
            )}
          </div>

          {/* Three column layout */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Column 1: Trust Score */}
            <div className="flex items-center justify-center rounded-2xl border border-atx-line bg-atx-panel/60 p-6">
              <TrustGauge
                score={currentScore}
                totalInteractions={currentInteractions.total}
              />
            </div>

            {/* Column 2: Category breakdown */}
            <div className="rounded-2xl border border-atx-line bg-atx-panel/60 p-6">
              <CategoryBreakdown categories={selectedAgent.categories} />
            </div>

            {/* Column 3: Interaction history */}
            <div className="rounded-2xl border border-atx-line bg-atx-panel/60 p-6">
              <InteractionDonut interactions={currentInteractions} />
            </div>
          </div>

          {/* Timeline chart */}
          <div className="mb-6 rounded-2xl border border-atx-line bg-atx-panel/60 p-6">
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
      <div className="rounded-2xl border border-atx-accent/30 bg-atx-accent/[0.05] px-6 py-12 text-center">
        <h2 className="text-[32px] font-medium leading-[1.15] tracking-[-0.8px] text-atx-ink [text-wrap:balance]">
          Build real reputation tracking for your AI agents
        </h2>
        <p className="mx-auto mb-8 mt-4 max-w-[640px] text-[17.5px] leading-[1.6] text-atx-ink-mid">
          Attestix provides cryptographically verifiable reputation scores,
          interaction logging, and trust attestations for any AI agent. Start
          building trust infrastructure in minutes.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <Link
            href="/docs/getting-started"
            className="inline-flex items-center gap-2 rounded-full bg-atx-accent px-6 py-3 text-[15px] font-medium text-[oklch(0.14_0.01_180)] transition-colors duration-200 hover:bg-atx-accent-deep"
          >
            Get started
            <ArrowRight className="h-4 w-4" />
          </Link>
          <Link
            href="/docs/guides/reputation"
            className="inline-flex items-center gap-2 rounded-full border border-atx-line px-6 py-3 text-[15px] font-medium text-atx-ink-mid transition-colors duration-200 hover:border-atx-ink-dim hover:text-atx-ink"
          >
            Reputation guide
          </Link>
        </div>
      </div>

      {/* Toast notifications */}
      <ToastContainer toasts={toasts} />
    </div>
  );
}
