"""Blockchain router - REST endpoints wrapping BlockchainService.

Anchors cryptographic hashes of off-chain artifacts (UAITs, VCs, audit log
batches) to Base L2 via Ethereum Attestation Service (EAS).
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.deps import get_blockchain_service, get_identity_service, get_credential_service
from services.blockchain_service import BlockchainService
from services.identity_service import IdentityService
from services.credential_service import CredentialService

logger = logging.getLogger("attestix.api.blockchain")

router = APIRouter(prefix="/v1/blockchain", tags=["blockchain"])


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class AnchorIdentityRequest(BaseModel):
    agent_id: str = Field(..., description="Agent ID whose identity to anchor on-chain")


class AnchorCredentialRequest(BaseModel):
    credential_id: str = Field(..., description="Credential URN to anchor on-chain (e.g., urn:uuid:...)")


class AnchorAuditBatchRequest(BaseModel):
    agent_id: str = Field(..., description="Agent ID whose audit log to batch-anchor")
    start_date: Optional[str] = Field(None, description="ISO date filter start (inclusive)")
    end_date: Optional[str] = Field(None, description="ISO date filter end (inclusive)")


class VerifyAnchorRequest(BaseModel):
    artifact_hash: str = Field(..., description="SHA-256 hash of the artifact to verify on-chain")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/anchor/identity", status_code=201)
def anchor_identity(
    body: AnchorIdentityRequest,
    bc_svc: BlockchainService = Depends(get_blockchain_service),
    id_svc: IdentityService = Depends(get_identity_service),
):
    """Anchor an agent identity (UAIT) hash to Base L2 via EAS.

    Computes SHA-256 of the full identity record and submits an on-chain attestation.
    """
    identity = id_svc.get_identity(body.agent_id)
    if not identity:
        raise HTTPException(status_code=404, detail=f"Identity {body.agent_id} not found")

    artifact_hash = bc_svc.hash_artifact(identity)
    result = bc_svc.anchor_artifact(
        artifact_hash=artifact_hash,
        artifact_type="identity",
        artifact_id=body.agent_id,
    )
    if isinstance(result, dict) and "error" in result:
        logger.warning("Identity anchor failed for %s: %s", body.agent_id, result["error"])
        raise HTTPException(status_code=400, detail="Identity anchoring failed")
    return result


@router.post("/anchor/credential", status_code=201)
def anchor_credential(
    body: AnchorCredentialRequest,
    bc_svc: BlockchainService = Depends(get_blockchain_service),
    cred_svc: CredentialService = Depends(get_credential_service),
):
    """Anchor a Verifiable Credential hash to Base L2 via EAS.

    Computes SHA-256 of the full VC and submits an on-chain attestation.
    """
    credential = cred_svc.get_credential(body.credential_id)
    if not credential:
        raise HTTPException(status_code=404, detail=f"Credential {body.credential_id} not found")

    artifact_hash = bc_svc.hash_artifact(credential)
    result = bc_svc.anchor_artifact(
        artifact_hash=artifact_hash,
        artifact_type="credential",
        artifact_id=body.credential_id,
    )
    if isinstance(result, dict) and "error" in result:
        logger.warning(
            "Credential anchor failed for %s: %s",
            body.credential_id, result["error"],
        )
        raise HTTPException(status_code=400, detail="Credential anchoring failed")
    return result


@router.post("/anchor/audit-batch", status_code=201)
def anchor_audit_batch(
    body: AnchorAuditBatchRequest,
    bc_svc: BlockchainService = Depends(get_blockchain_service),
):
    """Compute Merkle root of audit log entries and anchor on-chain."""
    result = bc_svc.anchor_audit_batch(
        agent_id=body.agent_id,
        start_date=body.start_date,
        end_date=body.end_date,
    )
    if isinstance(result, dict) and "error" in result:
        logger.warning(
            "Audit batch anchor failed for %s: %s",
            body.agent_id, result["error"],
        )
        raise HTTPException(status_code=400, detail="Audit batch anchoring failed")
    return result


@router.post("/verify/{anchor_id}")
def verify_anchor(
    anchor_id: str,
    body: VerifyAnchorRequest,
    bc_svc: BlockchainService = Depends(get_blockchain_service),
):
    """Verify an on-chain anchor for a given artifact hash.

    Checks local registry and verifies on-chain if blockchain is configured.
    """
    result = bc_svc.verify_anchor(body.artifact_hash)
    if isinstance(result, dict) and "error" in result:
        logger.warning("Anchor verification failed: %s", result["error"])
        raise HTTPException(status_code=400, detail="Anchor verification failed")
    return result


@router.get("/anchors/{anchor_id}")
def get_anchor_status(
    anchor_id: str,
    bc_svc: BlockchainService = Depends(get_blockchain_service),
):
    """Get all on-chain anchors associated with an agent.

    Note: anchor_id here is the agent_id used to look up anchors.
    """
    result = bc_svc.get_anchor_status(anchor_id)
    if isinstance(result, dict) and "error" in result:
        logger.error("Anchor status lookup failed for %s: %s", anchor_id, result["error"])
        raise HTTPException(status_code=500, detail="Anchor status lookup failed")
    return result


@router.get("/estimate-cost")
def estimate_anchor_cost(
    artifact_type: str = "identity",
    bc_svc: BlockchainService = Depends(get_blockchain_service),
):
    """Estimate gas cost for an anchoring transaction."""
    result = bc_svc.estimate_anchor_cost(artifact_type=artifact_type)
    if isinstance(result, dict) and "error" in result:
        logger.warning("Anchor cost estimation failed: %s", result["error"])
        raise HTTPException(status_code=400, detail="Anchor cost estimation failed")
    return result
