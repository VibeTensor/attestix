export interface AgentProfile {
  id: string;
  name: string;
  role: string;
  trustScore: number;
  categories: {
    compliance: number;
    accuracy: number;
    safety: number;
  };
  interactions: {
    total: number;
    success: number;
    partial: number;
    failure: number;
  };
  trend: "stable" | "improving" | "recovering" | "declining";
}

export const AGENTS: AgentProfile[] = [
  {
    id: "medassist-pro",
    name: "MedAssist Pro",
    role: "Medical diagnosis AI",
    trustScore: 0.92,
    categories: { compliance: 0.95, accuracy: 0.91, safety: 0.89 },
    interactions: { total: 47, success: 44, partial: 2, failure: 1 },
    trend: "stable",
  },
  {
    id: "codebot-v3",
    name: "CodeBot v3",
    role: "Code generation assistant",
    trustScore: 0.78,
    categories: { compliance: 0.82, accuracy: 0.76, safety: 0.80 },
    interactions: { total: 156, success: 121, partial: 28, failure: 7 },
    trend: "improving",
  },
  {
    id: "financegpt",
    name: "FinanceGPT",
    role: "Financial advisory bot",
    trustScore: 0.65,
    categories: { compliance: 0.71, accuracy: 0.58, safety: 0.73 },
    interactions: { total: 89, success: 58, partial: 19, failure: 12 },
    trend: "recovering",
  },
  {
    id: "contentcraft",
    name: "ContentCraft",
    role: "Marketing content generator",
    trustScore: 0.41,
    categories: { compliance: 0.35, accuracy: 0.48, safety: 0.45 },
    interactions: { total: 203, success: 82, partial: 65, failure: 56 },
    trend: "declining",
  },
  {
    id: "translateai",
    name: "TranslateAI",
    role: "Translation service",
    trustScore: 0.88,
    categories: { compliance: 0.90, accuracy: 0.87, safety: 0.92 },
    interactions: { total: 312, success: 287, partial: 20, failure: 5 },
    trend: "stable",
  },
];

/**
 * Generate 90 days of simulated trust score data based on trend profile.
 * Uses deterministic seeded randomness so data is consistent across renders.
 */
export function generateTimeline(
  agent: AgentProfile
): { day: number; score: number }[] {
  const points: { day: number; score: number }[] = [];
  const finalScore = agent.trustScore;

  // Seed a simple pseudo-random based on agent id
  let seed = 0;
  for (let i = 0; i < agent.id.length; i++) {
    seed = (seed * 31 + agent.id.charCodeAt(i)) & 0x7fffffff;
  }
  const random = () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff;
    return (seed % 10000) / 10000;
  };

  for (let day = 0; day < 90; day++) {
    const t = day / 89; // 0 to 1
    let baseScore: number;

    switch (agent.trend) {
      case "stable": {
        // Mostly flat around the final score with minor noise
        baseScore = finalScore + (random() - 0.5) * 0.04;
        break;
      }
      case "improving": {
        // Start lower, gradually improve
        const startScore = finalScore - 0.15;
        baseScore = startScore + (finalScore - startScore) * t + (random() - 0.5) * 0.03;
        break;
      }
      case "recovering": {
        // Start okay, dip around day 55-65, then recover
        const dipCenter = 60;
        const dipWidth = 15;
        const dipDepth = 0.18;
        const distFromDip = Math.abs(day - dipCenter);
        const dipFactor = distFromDip < dipWidth
          ? dipDepth * Math.cos((distFromDip / dipWidth) * Math.PI * 0.5)
          : 0;
        baseScore = finalScore + 0.05 - dipFactor + (random() - 0.5) * 0.03;
        break;
      }
      case "declining": {
        // Start higher, steadily decline
        const startHigh = finalScore + 0.22;
        baseScore = startHigh - (startHigh - finalScore) * t + (random() - 0.5) * 0.04;
        break;
      }
    }

    // Clamp between 0 and 1
    const clamped = Math.max(0, Math.min(1, baseScore));
    points.push({ day, score: Math.round(clamped * 1000) / 1000 });
  }

  return points;
}

/**
 * Recalculate trust score after a new interaction.
 * Uses exponential moving average with recent bias.
 */
export function recalculateScore(
  currentScore: number,
  outcome: "success" | "partial" | "failure"
): number {
  const outcomeWeight: Record<string, number> = {
    success: 1.0,
    partial: 0.5,
    failure: 0.0,
  };
  const alpha = 0.08; // learning rate for new interaction
  const outcomeValue = outcomeWeight[outcome];
  const newScore = currentScore * (1 - alpha) + outcomeValue * alpha;
  return Math.round(Math.max(0, Math.min(1, newScore)) * 100) / 100;
}

export function getTrustLabel(score: number): string {
  if (score > 0.7) return "Trusted";
  if (score >= 0.5) return "Moderate";
  return "At Risk";
}

export function getTrustColor(score: number): string {
  if (score > 0.7) return "text-emerald-400";
  if (score >= 0.5) return "text-yellow-400";
  return "text-red-400";
}

export function getTrustBgColor(score: number): string {
  if (score > 0.7) return "bg-emerald-400";
  if (score >= 0.5) return "bg-yellow-400";
  return "bg-red-400";
}

export function getTrustStroke(score: number): string {
  if (score > 0.7) return "#34d399";
  if (score >= 0.5) return "#facc15";
  return "#f87171";
}
