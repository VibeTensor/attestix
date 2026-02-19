"""Blockchain anchoring MCP tools for Attestix (6 tools).

Anchors off-chain artifacts (identities, credentials, audit batches) to
Base L2 via Ethereum Attestation Service (EAS) for tamper-proof verification.

Optional: all tools gracefully degrade if EVM_PRIVATE_KEY is not configured
or web3 is not installed.
"""

import json
from typing import Optional


def _validate_required(params: dict) -> str:
    for name, value in params.items():
        if not value or (isinstance(value, str) and not value.strip()):
            return json.dumps({"error": f"{name} cannot be empty"})
    return ""


def register(mcp):
    """Register blockchain anchoring tools with the MCP server."""

    @mcp.tool()
    async def anchor_identity(agent_id: str) -> str:
        """Anchor an agent identity (UAIT) hash to Base L2 via EAS.

        Computes SHA-256 of the full identity record and submits an
        on-chain attestation. Returns transaction hash and explorer URL.

        Args:
            agent_id: The Attestix agent ID (e.g., attestix:abc123...).
        """
        err = _validate_required({"agent_id": agent_id})
        if err:
            return err

        from services.cache import get_service
        from services.blockchain_service import BlockchainService
        from services.identity_service import IdentityService

        id_svc = get_service(IdentityService)
        identity = id_svc.get_identity(agent_id)
        if identity is None:
            return json.dumps({"error": f"Identity {agent_id} not found"})

        bc_svc = get_service(BlockchainService)
        artifact_hash = bc_svc.hash_artifact(identity)

        result = bc_svc.anchor_artifact(
            artifact_hash=artifact_hash,
            artifact_type="identity",
            artifact_id=agent_id,
        )
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def anchor_credential(credential_id: str) -> str:
        """Anchor a Verifiable Credential hash to Base L2 via EAS.

        Computes SHA-256 of the full VC and submits an on-chain attestation.
        Returns transaction hash and explorer URL.

        Args:
            credential_id: The credential URN (e.g., urn:uuid:...).
        """
        err = _validate_required({"credential_id": credential_id})
        if err:
            return err

        from services.cache import get_service
        from services.blockchain_service import BlockchainService
        from services.credential_service import CredentialService

        cred_svc = get_service(CredentialService)
        credential = cred_svc.get_credential(credential_id)
        if credential is None:
            return json.dumps({"error": f"Credential {credential_id} not found"})

        bc_svc = get_service(BlockchainService)
        artifact_hash = bc_svc.hash_artifact(credential)

        result = bc_svc.anchor_artifact(
            artifact_hash=artifact_hash,
            artifact_type="credential",
            artifact_id=credential_id,
        )
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def verify_anchor(
        artifact_id: str = "",
        artifact_hash: str = "",
    ) -> str:
        """Verify an on-chain anchor for an artifact.

        Provide either artifact_id (to look up and hash the artifact) or
        artifact_hash (direct SHA-256 hex) to check against on-chain records.

        Args:
            artifact_id: The artifact ID (agent ID or credential URN). Will be looked up and hashed.
            artifact_hash: Direct SHA-256 hex hash to verify. Use if you already have the hash.
        """
        if not artifact_id and not artifact_hash:
            return json.dumps({"error": "Provide either artifact_id or artifact_hash"})

        from services.cache import get_service
        from services.blockchain_service import BlockchainService

        bc_svc = get_service(BlockchainService)

        if artifact_id and not artifact_hash:
            # Try to resolve artifact_id to a hash
            artifact = None
            if artifact_id.startswith("attestix:"):
                from services.identity_service import IdentityService
                id_svc = get_service(IdentityService)
                artifact = id_svc.get_identity(artifact_id)
            elif artifact_id.startswith("urn:uuid:"):
                from services.credential_service import CredentialService
                cred_svc = get_service(CredentialService)
                artifact = cred_svc.get_credential(artifact_id)

            if artifact:
                artifact_hash = bc_svc.hash_artifact(artifact)
            else:
                # Fall back: search anchors.json by artifact_id
                from config import load_anchors
                data = load_anchors()
                matches = [
                    a for a in data["anchors"]
                    if a.get("artifact_id") == artifact_id
                ]
                if matches:
                    artifact_hash = matches[0]["artifact_hash"]
                else:
                    return json.dumps({
                        "error": f"Cannot resolve artifact_id '{artifact_id}' to a hash"
                    })

        result = bc_svc.verify_anchor(artifact_hash)
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def anchor_audit_batch(
        agent_id: str,
        start_date: str = "",
        end_date: str = "",
    ) -> str:
        """Anchor a batch of audit log entries as a Merkle root to Base L2.

        Computes a Merkle tree of all audit log entries for the agent in the
        given date range and anchors the root hash on-chain. This provides
        tamper-evident proof for Article 12 audit trails.

        Args:
            agent_id: The Attestix agent ID.
            start_date: ISO date for start of range (e.g., 2026-01-01T00:00:00). Empty = all.
            end_date: ISO date for end of range. Empty = all.
        """
        err = _validate_required({"agent_id": agent_id})
        if err:
            return err

        from services.cache import get_service
        from services.blockchain_service import BlockchainService

        bc_svc = get_service(BlockchainService)
        result = bc_svc.anchor_audit_batch(
            agent_id=agent_id,
            start_date=start_date or None,
            end_date=end_date or None,
        )
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def get_anchor_status(agent_id: str) -> str:
        """Get all on-chain anchors for an agent, grouped by type.

        Shows identity anchors, credential anchors, and audit batch anchors
        with transaction hashes, explorer URLs, and timestamps.

        Args:
            agent_id: The Attestix agent ID.
        """
        err = _validate_required({"agent_id": agent_id})
        if err:
            return err

        from services.cache import get_service
        from services.blockchain_service import BlockchainService

        bc_svc = get_service(BlockchainService)
        result = bc_svc.get_anchor_status(agent_id)
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def estimate_anchor_cost(artifact_type: str = "identity") -> str:
        """Estimate gas cost for an anchoring transaction on Base L2.

        Shows current gas price, wallet balance, estimated cost in ETH,
        and whether the wallet has sufficient funds.

        Args:
            artifact_type: Type of artifact to estimate for (identity, credential, declaration, audit_batch).
        """
        from services.cache import get_service
        from services.blockchain_service import BlockchainService

        bc_svc = get_service(BlockchainService)
        result = bc_svc.estimate_anchor_cost(artifact_type)
        return json.dumps(result, indent=2, default=str)
