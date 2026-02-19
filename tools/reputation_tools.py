"""Reputation MCP tools for Attestix (3 tools)."""

import json


def register(mcp):
    """Register reputation tools with the MCP server."""

    @mcp.tool()
    async def record_interaction(
        agent_id: str,
        counterparty_id: str,
        outcome: str,
        category: str = "general",
        details: str = "",
    ) -> str:
        """Record an interaction outcome and update the agent's trust score.

        Args:
            agent_id: The agent being evaluated.
            counterparty_id: The other party in the interaction.
            outcome: One of: success, failure, partial, timeout.
            category: Interaction category (e.g., task, delegation, general).
            details: Optional description of what happened.
        """
        from services.cache import get_service
        from services.reputation_service import ReputationService

        svc = get_service(ReputationService)
        result = svc.record_interaction(
            agent_id=agent_id,
            counterparty_id=counterparty_id,
            outcome=outcome,
            category=category,
            details=details,
        )
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def get_reputation(agent_id: str) -> str:
        """Get the trust score and interaction history for an agent.

        Returns a recency-weighted score from 0.0 to 1.0 with category breakdown.

        Args:
            agent_id: The Attestix agent ID to check.
        """
        from services.cache import get_service
        from services.reputation_service import ReputationService

        svc = get_service(ReputationService)
        result = svc.get_reputation(agent_id)
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def query_reputation(
        min_score: float = 0.0,
        max_score: float = 1.0,
        min_interactions: int = 0,
        category: str = "",
        limit: int = 50,
    ) -> str:
        """Search for agents by reputation criteria.

        Args:
            min_score: Minimum trust score (0.0 - 1.0).
            max_score: Maximum trust score (0.0 - 1.0).
            min_interactions: Minimum number of recorded interactions.
            category: Filter by interaction category (empty = all).
            limit: Maximum results to return.
        """
        from services.cache import get_service
        from services.reputation_service import ReputationService

        svc = get_service(ReputationService)
        results = svc.query_reputation(
            min_score=min_score,
            max_score=max_score,
            min_interactions=min_interactions,
            category=category or None,
            limit=limit,
        )
        return json.dumps(results, indent=2, default=str)
