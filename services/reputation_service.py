"""Reputation and trust scoring service for AURA Protocol.

Records agent interactions and computes recency-weighted trust scores
with exponential decay (30-day half-life).
"""

import math
import time
from datetime import datetime, timezone
from typing import List, Optional

from config import load_reputation, save_reputation
from errors import ErrorCategory, log_and_format_error

# Scoring constants
HALF_LIFE_DAYS = 30
DECAY_LAMBDA = math.log(2) / (HALF_LIFE_DAYS * 86400)  # per second

OUTCOME_WEIGHTS = {
    "success": 1.0,
    "partial": 0.5,
    "failure": 0.0,
    "timeout": 0.2,
}


class ReputationService:
    """Manages agent reputation through interaction tracking."""

    def record_interaction(
        self,
        agent_id: str,
        counterparty_id: str,
        outcome: str,
        category: str = "general",
        details: str = "",
    ) -> dict:
        """Record an interaction and update trust scores.

        Args:
            agent_id: The agent being evaluated.
            counterparty_id: The other party in the interaction.
            outcome: One of 'success', 'failure', 'partial', 'timeout'.
            category: Interaction category (e.g., 'task', 'delegation', 'general').
            details: Optional free-text details.
        """
        try:
            if outcome not in OUTCOME_WEIGHTS:
                return {"error": f"Invalid outcome '{outcome}'. Use: {list(OUTCOME_WEIGHTS.keys())}"}

            now = datetime.now(timezone.utc)
            interaction = {
                "agent_id": agent_id,
                "counterparty_id": counterparty_id,
                "outcome": outcome,
                "category": category,
                "details": details,
                "timestamp": now.isoformat(),
                "epoch": int(now.timestamp()),
            }

            data = load_reputation()
            data["interactions"].append(interaction)

            # Recompute score for this agent
            score = self._compute_score(data["interactions"], agent_id)
            data["scores"][agent_id] = {
                "trust_score": round(score, 4),
                "last_updated": now.isoformat(),
                "total_interactions": sum(
                    1 for i in data["interactions"] if i["agent_id"] == agent_id
                ),
            }

            save_reputation(data)

            return {
                "recorded": True,
                "interaction": interaction,
                "updated_score": data["scores"][agent_id],
            }
        except Exception as e:
            return {
                "error": log_and_format_error(
                    "record_interaction", e, ErrorCategory.REPUTATION,
                    agent_id=agent_id,
                )
            }

    def get_reputation(self, agent_id: str) -> dict:
        """Get the current trust score for an agent."""
        try:
            data = load_reputation()

            # Get cached score or compute fresh
            agent_interactions = [
                i for i in data["interactions"] if i["agent_id"] == agent_id
            ]

            if not agent_interactions:
                return {
                    "agent_id": agent_id,
                    "trust_score": None,
                    "total_interactions": 0,
                    "message": "No interactions recorded for this agent.",
                }

            score = self._compute_score(data["interactions"], agent_id)

            # Category breakdown
            categories = {}
            for i in agent_interactions:
                cat = i.get("category", "general")
                if cat not in categories:
                    categories[cat] = {"success": 0, "failure": 0, "partial": 0, "timeout": 0, "total": 0}
                categories[cat][i["outcome"]] += 1
                categories[cat]["total"] += 1

            return {
                "agent_id": agent_id,
                "trust_score": round(score, 4),
                "total_interactions": len(agent_interactions),
                "category_breakdown": categories,
                "last_interaction": agent_interactions[-1]["timestamp"],
            }
        except Exception as e:
            return {
                "error": log_and_format_error(
                    "get_reputation", e, ErrorCategory.REPUTATION,
                    agent_id=agent_id,
                )
            }

    def query_reputation(
        self,
        min_score: float = 0.0,
        max_score: float = 1.0,
        min_interactions: int = 0,
        category: Optional[str] = None,
        limit: int = 50,
    ) -> List[dict]:
        """Search agents by reputation criteria."""
        try:
            data = load_reputation()

            # Get all unique agent IDs
            agent_ids = set(i["agent_id"] for i in data["interactions"])

            results = []
            for aid in agent_ids:
                agent_interactions = [
                    i for i in data["interactions"] if i["agent_id"] == aid
                ]

                # Filter by category
                if category:
                    agent_interactions = [
                        i for i in agent_interactions if i.get("category") == category
                    ]

                if len(agent_interactions) < min_interactions:
                    continue

                score = self._compute_score(
                    agent_interactions if category else data["interactions"],
                    aid,
                )

                if min_score <= score <= max_score:
                    results.append({
                        "agent_id": aid,
                        "trust_score": round(score, 4),
                        "interaction_count": len(agent_interactions),
                    })

                if len(results) >= limit:
                    break

            # Sort by score descending
            results.sort(key=lambda x: x["trust_score"], reverse=True)
            return results
        except Exception as e:
            return [{
                "error": log_and_format_error(
                    "query_reputation", e, ErrorCategory.REPUTATION,
                )
            }]

    def _compute_score(self, all_interactions: list, agent_id: str) -> float:
        """Compute recency-weighted trust score (0.0 - 1.0).

        Uses exponential decay with 30-day half-life:
        weight = exp(-lambda * age_seconds)
        score = sum(outcome_weight * decay_weight) / sum(decay_weight)
        """
        now = time.time()
        agent_interactions = [
            i for i in all_interactions if i["agent_id"] == agent_id
        ]

        if not agent_interactions:
            return 0.0

        weighted_sum = 0.0
        weight_total = 0.0

        for interaction in agent_interactions:
            epoch = interaction.get("epoch", 0)
            age = max(now - epoch, 0)
            decay = math.exp(-DECAY_LAMBDA * age)

            outcome = interaction.get("outcome", "failure")
            outcome_val = OUTCOME_WEIGHTS.get(outcome, 0.0)

            weighted_sum += outcome_val * decay
            weight_total += decay

        if weight_total == 0:
            return 0.0

        return weighted_sum / weight_total
