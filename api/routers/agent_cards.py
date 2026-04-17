"""Agent Cards router - REST endpoints wrapping AgentCardService.

Discover, parse, and generate Google A2A Agent Cards
(the /.well-known/agent.json standard).
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.deps import get_agent_card_service
from services.agent_card_service import AgentCardService

logger = logging.getLogger("attestix.api.agent_cards")

router = APIRouter(prefix="/v1/agent-cards", tags=["agent-cards"])


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class DiscoverAgentRequest(BaseModel):
    base_url: str = Field(
        ...,
        description="HTTPS base URL of the agent to discover (e.g., https://example.com)",
    )


class ParseAgentCardRequest(BaseModel):
    card: Dict = Field(..., description="Raw A2A Agent Card JSON to parse")


class SkillDefinition(BaseModel):
    id: str = Field(..., description="Unique skill identifier")
    name: str = Field(..., description="Human-readable skill name")
    description: str = Field("", description="What this skill does")


class GenerateAgentCardRequest(BaseModel):
    name: str = Field(..., description="Agent display name")
    url: str = Field(..., description="Base URL where the agent is hosted")
    description: str = Field("", description="What the agent does")
    skills: Optional[List[SkillDefinition]] = Field(
        None, description="List of agent skills/capabilities",
    )
    version: str = Field("1.0.0", description="Agent version string")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/discover")
def discover_agent(
    body: DiscoverAgentRequest,
    svc: AgentCardService = Depends(get_agent_card_service),
):
    """Fetch and parse an A2A Agent Card from /.well-known/agent.json.

    Performs SSRF validation and only allows HTTPS URLs.
    """
    result = svc.discover_agent(body.base_url)
    if isinstance(result, dict) and "error" in result:
        error_msg = result["error"]
        logger.warning("Agent discovery failed for %s: %s", body.base_url, error_msg)
        if "timeout" in error_msg.lower():
            raise HTTPException(status_code=504, detail="Agent discovery timed out")
        if "http" in error_msg.lower() and any(c.isdigit() for c in error_msg):
            raise HTTPException(status_code=502, detail="Upstream agent discovery error")
        raise HTTPException(status_code=400, detail="Agent discovery failed")
    return result


@router.post("/parse")
def parse_agent_card(
    body: ParseAgentCardRequest,
    svc: AgentCardService = Depends(get_agent_card_service),
):
    """Parse a raw A2A Agent Card JSON into normalized fields.

    Useful when you already have the card and want structured data.
    """
    result = svc.parse_agent_card(body.card)
    if isinstance(result, dict) and "error" in result:
        logger.warning("Agent card parsing failed: %s", result["error"])
        raise HTTPException(status_code=400, detail="Agent card parsing failed")
    return result


@router.post("/generate", status_code=201)
def generate_agent_card(
    body: GenerateAgentCardRequest,
    svc: AgentCardService = Depends(get_agent_card_service),
):
    """Generate a valid A2A Agent Card JSON (agent.json).

    Returns the card JSON and hosting instructions for .well-known/agent.json.
    """
    skills_dicts = None
    if body.skills:
        skills_dicts = [s.model_dump() for s in body.skills]

    result = svc.generate_agent_card(
        name=body.name,
        url=body.url,
        description=body.description,
        skills=skills_dicts,
        version=body.version,
    )
    if isinstance(result, dict) and "error" in result:
        logger.warning("Agent card generation failed: %s", result["error"])
        raise HTTPException(status_code=400, detail="Agent card generation failed")
    return result
