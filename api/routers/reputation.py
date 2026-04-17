"""Reputation router - REST endpoints wrapping ReputationService.

Records agent interactions and queries recency-weighted trust scores
with exponential decay (30-day half-life).
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.deps import get_reputation_service
from services.reputation_service import ReputationService

logger = logging.getLogger("attestix.api.reputation")

router = APIRouter(prefix="/v1/reputation", tags=["reputation"])


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class RecordInteractionRequest(BaseModel):
    agent_id: str = Field(..., description="The agent being evaluated")
    counterparty_id: str = Field(..., description="The other party in the interaction")
    outcome: str = Field(..., description="Interaction outcome: success, failure, partial, or timeout")
    category: str = Field("general", description="Interaction category (e.g., task, delegation, general)")
    details: str = Field("", description="Optional free-text details")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/interactions", status_code=201)
def record_interaction(
    body: RecordInteractionRequest,
    svc: ReputationService = Depends(get_reputation_service),
):
    """Record an interaction and update trust scores."""
    result = svc.record_interaction(
        agent_id=body.agent_id,
        counterparty_id=body.counterparty_id,
        outcome=body.outcome,
        category=body.category,
        details=body.details,
    )
    if isinstance(result, dict) and "error" in result:
        logger.warning("Interaction recording failed: %s", result["error"])
        raise HTTPException(status_code=400, detail="Interaction recording failed")
    return result


@router.get("/{agent_id}")
def get_reputation(
    agent_id: str,
    svc: ReputationService = Depends(get_reputation_service),
):
    """Get the current trust score and category breakdown for an agent."""
    result = svc.get_reputation(agent_id)
    if isinstance(result, dict) and "error" in result:
        logger.error("Reputation lookup failed for %s: %s", agent_id, result["error"])
        raise HTTPException(status_code=500, detail="Reputation lookup failed")
    return result


@router.get("")
def query_reputation(
    min_score: float = 0.0,
    max_score: float = 1.0,
    min_interactions: int = 0,
    category: Optional[str] = None,
    limit: int = 50,
    svc: ReputationService = Depends(get_reputation_service),
):
    """Search agents by reputation criteria."""
    results = svc.query_reputation(
        min_score=min_score,
        max_score=max_score,
        min_interactions=min_interactions,
        category=category,
        limit=limit,
    )
    if results and isinstance(results[0], dict) and "error" in results[0]:
        logger.error("Reputation query failed: %s", results[0]["error"])
        raise HTTPException(status_code=500, detail="Reputation query failed")
    return results
