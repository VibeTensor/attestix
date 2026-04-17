"""Credentials router - REST endpoints wrapping CredentialService.

Issues, verifies, and manages W3C Verifiable Credentials (VC Data Model 1.1)
with Ed25519Signature2020 proofs.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.deps import get_credential_service
from services.credential_service import CredentialService

logger = logging.getLogger("attestix.api.credentials")

router = APIRouter(prefix="/v1", tags=["credentials"])


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class IssueCredentialRequest(BaseModel):
    subject_id: str = Field(..., description="Agent ID the credential is issued to")
    credential_type: str = Field(..., description="Credential type (e.g., AgentIdentityCredential)")
    issuer_name: str = Field(..., description="Name of the credential issuer")
    claims: Dict = Field(..., description="Claims to include in the credential subject")
    expiry_days: int = Field(365, description="Days until the credential expires")


class RevokeCredentialRequest(BaseModel):
    reason: str = Field("", description="Reason for revocation")


class VerifyExternalCredentialRequest(BaseModel):
    credential: Dict = Field(..., description="Raw W3C Verifiable Credential JSON to verify")


class CreatePresentationRequest(BaseModel):
    agent_id: str = Field(..., description="Agent ID (holder) creating the presentation")
    credential_ids: List[str] = Field(..., description="List of credential URNs to include")
    audience_did: str = Field("", description="DID of the intended verifier (domain binding)")
    challenge: str = Field("", description="Challenge nonce for replay protection")


# ---------------------------------------------------------------------------
# Credential endpoints
# ---------------------------------------------------------------------------

@router.post("/credentials", status_code=201)
def issue_credential(
    body: IssueCredentialRequest,
    svc: CredentialService = Depends(get_credential_service),
):
    """Issue a W3C Verifiable Credential with Ed25519Signature2020 proof."""
    result = svc.issue_credential(
        subject_id=body.subject_id,
        credential_type=body.credential_type,
        issuer_name=body.issuer_name,
        claims=body.claims,
        expiry_days=body.expiry_days,
    )
    if isinstance(result, dict) and "error" in result:
        logger.warning("Credential issuance failed: %s", result["error"])
        raise HTTPException(status_code=400, detail="Credential issuance failed")
    return result


@router.get("/credentials")
def list_credentials(
    agent_id: Optional[str] = None,
    credential_type: Optional[str] = None,
    valid_only: bool = False,
    limit: int = 50,
    svc: CredentialService = Depends(get_credential_service),
):
    """List credentials with optional filters."""
    results = svc.list_credentials(
        agent_id=agent_id,
        credential_type=credential_type,
        valid_only=valid_only,
        limit=limit,
    )
    # Service returns list with error dict on failure
    if results and isinstance(results[0], dict) and "error" in results[0]:
        logger.error("Credential listing failed: %s", results[0]["error"])
        raise HTTPException(status_code=500, detail="Credential listing failed")
    return results


@router.post("/credentials/verify-external")
def verify_credential_external(
    body: VerifyExternalCredentialRequest,
    svc: CredentialService = Depends(get_credential_service),
):
    """Verify a credential provided as raw JSON (for external verifiers).

    Does not require the credential to be in local storage.
    """
    result = svc.verify_credential_external(body.credential)
    if isinstance(result, dict) and "error" in result:
        logger.warning("External credential verification failed: %s", result["error"])
        raise HTTPException(status_code=400, detail="Credential verification failed")
    return result


@router.get("/credentials/{credential_id:path}")
def get_credential(
    credential_id: str,
    svc: CredentialService = Depends(get_credential_service),
):
    """Get a credential by ID (e.g., urn:uuid:...)."""
    result = svc.get_credential(credential_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Credential {credential_id} not found")
    return result


@router.post("/credentials/{credential_id:path}/verify")
def verify_credential(
    credential_id: str,
    svc: CredentialService = Depends(get_credential_service),
):
    """Verify a credential by ID: check signature, expiry, and revocation."""
    result = svc.verify_credential(credential_id)
    if isinstance(result, dict) and "error" in result:
        logger.warning("Credential verification failed for %s: %s", credential_id, result["error"])
        raise HTTPException(status_code=400, detail="Credential verification failed")
    return result


@router.delete("/credentials/{credential_id:path}")
def revoke_credential(
    credential_id: str,
    body: Optional[RevokeCredentialRequest] = None,
    svc: CredentialService = Depends(get_credential_service),
):
    """Revoke a credential."""
    reason = body.reason if body else ""
    result = svc.revoke_credential(credential_id, reason=reason)
    if isinstance(result, dict) and "error" in result:
        error_msg = result["error"]
        logger.warning("Credential revocation failed for %s: %s", credential_id, error_msg)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail="Credential not found")
        raise HTTPException(status_code=400, detail="Credential revocation failed")
    return result


# ---------------------------------------------------------------------------
# Presentation endpoints
# ---------------------------------------------------------------------------

@router.post("/presentations", status_code=201)
def create_verifiable_presentation(
    body: CreatePresentationRequest,
    svc: CredentialService = Depends(get_credential_service),
):
    """Bundle multiple VCs into a Verifiable Presentation for a verifier."""
    result = svc.create_verifiable_presentation(
        agent_id=body.agent_id,
        credential_ids=body.credential_ids,
        audience_did=body.audience_did,
        challenge=body.challenge,
    )
    if isinstance(result, dict) and "error" in result:
        error_msg = result["error"]
        logger.warning("Verifiable presentation creation failed: %s", error_msg)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail="Credential or agent not found")
        raise HTTPException(status_code=400, detail="Verifiable presentation creation failed")
    return result
