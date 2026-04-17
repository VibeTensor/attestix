"""Identity router - REST endpoints wrapping IdentityService.

Manages Unified Agent Identity Tokens (UAITs): create, read, list,
verify, translate, revoke, and GDPR purge.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator

from api.deps import get_identity_service
from services.identity_service import IdentityService

logger = logging.getLogger("attestix.api.identity")

router = APIRouter(prefix="/v1/identities", tags=["identity"])


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

#: Maximum allowed length for an agent display name (defense in depth against
#: UI abuse, log-injection, and storage bloat).
MAX_DISPLAY_NAME_LENGTH = 500


class CreateIdentityRequest(BaseModel):
    display_name: str = Field(
        ...,
        min_length=1,
        max_length=MAX_DISPLAY_NAME_LENGTH,
        description="Human-readable name for the agent (1-500 characters, non-empty)",
    )
    source_protocol: str = Field(..., description="Identity source protocol (e.g., oauth2, api_key, did)")
    identity_token: str = Field("", description="Optional identity token to extract info from")
    capabilities: Optional[List[str]] = Field(None, description="List of capability strings")
    description: str = Field("", description="Description of the agent")
    issuer_name: str = Field("", description="Name of the identity issuer")
    expiry_days: Optional[int] = Field(None, description="Days until the identity expires")

    @field_validator("display_name")
    @classmethod
    def _validate_display_name(cls, value: str) -> str:
        if value is None:
            raise ValueError("display_name is required")
        stripped = value.strip()
        if not stripped:
            raise ValueError("display_name must not be empty or whitespace-only")
        if len(stripped) > MAX_DISPLAY_NAME_LENGTH:
            raise ValueError(
                f"display_name must be at most {MAX_DISPLAY_NAME_LENGTH} characters"
            )
        # Reject control characters that could break logs, JSON, or terminals.
        if any(ord(ch) < 0x20 and ch not in ("\t",) for ch in stripped):
            raise ValueError("display_name contains disallowed control characters")
        return stripped


class TranslateIdentityRequest(BaseModel):
    target_format: str = Field(
        ...,
        description="Target format: a2a_agent_card, did_document, oauth_claims, or summary",
    )


class RevokeIdentityRequest(BaseModel):
    reason: str = Field("", description="Reason for revocation")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", status_code=201)
def create_identity(
    body: CreateIdentityRequest,
    svc: IdentityService = Depends(get_identity_service),
):
    """Create a new Unified Agent Identity Token (UAIT)."""
    result = svc.create_identity(
        display_name=body.display_name,
        source_protocol=body.source_protocol,
        identity_token=body.identity_token,
        capabilities=body.capabilities,
        description=body.description,
        issuer_name=body.issuer_name,
        expiry_days=body.expiry_days,
    )
    if isinstance(result, dict) and "error" in result:
        logger.warning("Identity creation failed: %s", result["error"])
        raise HTTPException(status_code=400, detail="Identity creation failed")
    return result


@router.get("")
def list_identities(
    source_protocol: Optional[str] = None,
    include_revoked: bool = False,
    limit: int = 50,
    svc: IdentityService = Depends(get_identity_service),
):
    """List UAITs with optional filters."""
    return svc.list_identities(
        source_protocol=source_protocol,
        include_revoked=include_revoked,
        limit=limit,
    )


@router.get("/{agent_id}")
def get_identity(
    agent_id: str,
    svc: IdentityService = Depends(get_identity_service),
):
    """Get a single UAIT by agent_id."""
    result = svc.get_identity(agent_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Identity {agent_id} not found")
    return result


@router.post("/{agent_id}/verify")
def verify_identity(
    agent_id: str,
    svc: IdentityService = Depends(get_identity_service),
):
    """Verify a UAIT: check existence, revocation, expiry, and signature."""
    return svc.verify_identity(agent_id)


@router.post("/{agent_id}/translate")
def translate_identity(
    agent_id: str,
    body: TranslateIdentityRequest,
    svc: IdentityService = Depends(get_identity_service),
):
    """Convert a UAIT to another format (A2A, DID Document, OAuth, summary)."""
    result = svc.translate_identity(agent_id, body.target_format)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Identity {agent_id} not found")
    if isinstance(result, dict) and "error" in result:
        logger.warning(
            "Identity translation failed for %s: %s",
            agent_id, result["error"],
        )
        raise HTTPException(status_code=400, detail="Identity translation failed")
    return result


@router.delete("/{agent_id}")
def revoke_identity(
    agent_id: str,
    body: Optional[RevokeIdentityRequest] = None,
    svc: IdentityService = Depends(get_identity_service),
):
    """Revoke a UAIT."""
    reason = body.reason if body else ""
    result = svc.revoke_identity(agent_id, reason=reason)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Identity {agent_id} not found")
    return result


@router.delete("/{agent_id}/purge")
def purge_agent_data(
    agent_id: str,
    svc: IdentityService = Depends(get_identity_service),
):
    """GDPR Article 17 - Right to erasure. Purge all data for an agent."""
    result = svc.purge_agent_data(agent_id)
    if isinstance(result, dict) and "error" in result:
        logger.warning(
            "Agent data purge failed for %s: %s",
            agent_id, result["error"],
        )
        raise HTTPException(status_code=400, detail="Agent data purge failed")
    return result
