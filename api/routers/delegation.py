"""Delegation router - REST endpoints wrapping DelegationService.

Creates, verifies, and manages UCAN-style JWT delegation tokens
with capability attenuation.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.deps import get_delegation_service
from services.delegation_service import DelegationService

logger = logging.getLogger("attestix.api.delegation")

router = APIRouter(prefix="/v1/delegations", tags=["delegation"])


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class CreateDelegationRequest(BaseModel):
    issuer_agent_id: str = Field(..., description="Agent granting capabilities")
    audience_agent_id: str = Field(..., description="Agent receiving capabilities")
    capabilities: List[str] = Field(..., description="List of capability strings being delegated")
    expiry_hours: int = Field(24, description="Hours until the delegation expires")
    parent_token: Optional[str] = Field(None, description="Optional parent delegation token for chaining")


class VerifyDelegationRequest(BaseModel):
    token: str = Field(..., description="UCAN delegation JWT to verify")


class RevokeDelegationRequest(BaseModel):
    reason: str = Field("", description="Reason for revocation")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", status_code=201)
def create_delegation(
    body: CreateDelegationRequest,
    svc: DelegationService = Depends(get_delegation_service),
):
    """Create a UCAN-style delegation JWT."""
    result = svc.create_delegation(
        issuer_agent_id=body.issuer_agent_id,
        audience_agent_id=body.audience_agent_id,
        capabilities=body.capabilities,
        expiry_hours=body.expiry_hours,
        parent_token=body.parent_token,
    )
    if isinstance(result, dict) and "error" in result:
        logger.warning("Delegation creation failed: %s", result["error"])
        raise HTTPException(status_code=400, detail="Delegation creation failed")
    return result


@router.get("")
def list_delegations(
    agent_id: Optional[str] = None,
    role: str = "any",
    include_expired: bool = False,
    svc: DelegationService = Depends(get_delegation_service),
):
    """List delegation records with optional filters.

    role can be 'issuer', 'audience', or 'any'.
    """
    return svc.list_delegations(
        agent_id=agent_id,
        role=role,
        include_expired=include_expired,
    )


@router.post("/verify")
def verify_delegation(
    body: VerifyDelegationRequest,
    svc: DelegationService = Depends(get_delegation_service),
):
    """Verify a UCAN delegation token (signature, expiry, revocation)."""
    result = svc.verify_delegation(body.token)
    if isinstance(result, dict) and "error" in result:
        logger.warning("Delegation verification failed: %s", result["error"])
        raise HTTPException(status_code=400, detail="Delegation verification failed")
    return result


@router.delete("/{delegation_id}")
def revoke_delegation(
    delegation_id: str,
    body: Optional[RevokeDelegationRequest] = None,
    svc: DelegationService = Depends(get_delegation_service),
):
    """Revoke a delegation by its JTI (JWT ID)."""
    reason = body.reason if body else ""
    result = svc.revoke_delegation(delegation_id, reason=reason)
    if isinstance(result, dict) and "error" in result:
        logger.warning("Delegation revocation failed for %s: %s", delegation_id, result["error"])
        if "not found" in result["error"].lower():
            raise HTTPException(status_code=404, detail="Delegation not found")
        raise HTTPException(status_code=400, detail="Delegation revocation failed")
    return result
