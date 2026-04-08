"""DID router - REST endpoints wrapping DIDService.

Supports creating and resolving Decentralized Identifiers:
did:key (Ed25519), did:web, and Universal Resolver fallback.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.deps import get_did_service
from services.did_service import DIDService

logger = logging.getLogger("attestix.api.did")

router = APIRouter(prefix="/v1/dids", tags=["did"])


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class CreateDIDWebRequest(BaseModel):
    domain: str = Field(..., description="Domain to host the DID document (e.g., example.com)")
    path: str = Field("", description="Optional path component (e.g., agents/myagent)")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/key", status_code=201)
def create_did_key(
    svc: DIDService = Depends(get_did_service),
):
    """Generate a new ephemeral did:key with Ed25519 keypair.

    The private key is stored locally in .keypairs.json, never returned in the response.
    """
    result = svc.create_did_key()
    if isinstance(result, dict) and "error" in result:
        logger.error("DID key creation failed: %s", result["error"])
        raise HTTPException(status_code=500, detail="DID key creation failed")
    return result


@router.post("/web", status_code=201)
def create_did_web(
    body: CreateDIDWebRequest,
    svc: DIDService = Depends(get_did_service),
):
    """Generate a did:web DID Document for self-hosting.

    The returned document must be hosted at the appropriate .well-known URL.
    """
    result = svc.create_did_web(domain=body.domain, path=body.path)
    if isinstance(result, dict) and "error" in result:
        logger.error("DID web creation failed: %s", result["error"])
        raise HTTPException(status_code=500, detail="DID web creation failed")
    return result


@router.get("/resolve/{did:path}")
def resolve_did(
    did: str,
    svc: DIDService = Depends(get_did_service),
):
    """Resolve a DID to its DID Document.

    Supports did:key (local), did:web (HTTP), and Universal Resolver fallback.
    """
    result = svc.resolve_did(did)
    if isinstance(result, dict) and "error" in result:
        error_msg = result["error"]
        logger.warning("DID resolution failed for %s: %s", did, error_msg)
        if "timeout" in error_msg.lower():
            raise HTTPException(status_code=504, detail="DID resolution timed out")
        if "http" in error_msg.lower() and any(c.isdigit() for c in error_msg):
            raise HTTPException(status_code=502, detail="Upstream DID resolution error")
        raise HTTPException(status_code=400, detail="DID resolution failed")
    return result
