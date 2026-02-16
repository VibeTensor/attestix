"""Credential MCP tools for AURA Protocol (6 tools).

W3C Verifiable Credentials (VC Data Model 2.0) issuance and verification.
"""

import json
from typing import Optional


def register(mcp):
    """Register credential tools with the MCP server."""

    @mcp.tool()
    async def issue_credential(
        subject_agent_id: str,
        credential_type: str,
        issuer_name: str,
        claims_json: str,
        expiry_days: int = 365,
    ) -> str:
        """Issue a W3C Verifiable Credential with Ed25519Signature2020 proof.

        Args:
            subject_agent_id: The AURA agent ID this credential is about.
            credential_type: Credential type (e.g., EUAIActComplianceCredential, AgentIdentityCredential).
            issuer_name: Name of the issuing authority.
            claims_json: JSON string of credential claims (e.g., {"compliant": true, "risk_level": "high"}).
            expiry_days: Days until credential expires (default 365).
        """
        from services.cache import get_service
        from services.credential_service import CredentialService

        svc = get_service(CredentialService)
        try:
            claims = json.loads(claims_json)
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON in claims_json"})

        result = svc.issue_credential(
            subject_id=subject_agent_id,
            credential_type=credential_type,
            issuer_name=issuer_name,
            claims=claims,
            expiry_days=expiry_days,
        )
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def verify_credential(credential_id: str) -> str:
        """Verify a Verifiable Credential: check signature, expiry, and revocation.

        Args:
            credential_id: The credential URN (e.g., urn:uuid:...).
        """
        from services.cache import get_service
        from services.credential_service import CredentialService

        svc = get_service(CredentialService)
        result = svc.verify_credential(credential_id)
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def revoke_credential(credential_id: str, reason: str = "") -> str:
        """Revoke a Verifiable Credential.

        Args:
            credential_id: The credential URN to revoke.
            reason: Why the credential is being revoked.
        """
        from services.cache import get_service
        from services.credential_service import CredentialService

        svc = get_service(CredentialService)
        result = svc.revoke_credential(credential_id, reason)
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def get_credential(credential_id: str) -> str:
        """Get full details of a Verifiable Credential.

        Args:
            credential_id: The credential URN.
        """
        from services.cache import get_service
        from services.credential_service import CredentialService

        svc = get_service(CredentialService)
        result = svc.get_credential(credential_id)
        if result is None:
            return json.dumps({"error": f"Credential {credential_id} not found"})
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def list_credentials(
        agent_id: str = "",
        credential_type: str = "",
        valid_only: bool = False,
        limit: int = 50,
    ) -> str:
        """List Verifiable Credentials with optional filters.

        Args:
            agent_id: Filter by subject agent ID. Empty = all agents.
            credential_type: Filter by type (e.g., EUAIActComplianceCredential). Empty = all types.
            valid_only: Only return non-revoked, non-expired credentials.
            limit: Maximum number of results.
        """
        from services.cache import get_service
        from services.credential_service import CredentialService

        svc = get_service(CredentialService)
        results = svc.list_credentials(
            agent_id=agent_id or None,
            credential_type=credential_type or None,
            valid_only=valid_only,
            limit=limit,
        )
        return json.dumps(results, indent=2, default=str)

    @mcp.tool()
    async def create_verifiable_presentation(
        agent_id: str,
        credential_ids: str,
        audience_did: str = "",
    ) -> str:
        """Bundle multiple Verifiable Credentials into a Verifiable Presentation.

        Creates a signed VP that an agent can present to a verifier to prove compliance.

        Args:
            agent_id: The AURA agent ID (holder/presenter).
            credential_ids: Comma-separated credential URNs to include.
            audience_did: DID of the intended verifier (optional).
        """
        from services.cache import get_service
        from services.credential_service import CredentialService

        svc = get_service(CredentialService)
        ids = [c.strip() for c in credential_ids.split(",") if c.strip()]
        if not ids:
            return json.dumps({"error": "No credential_ids provided"})

        result = svc.create_verifiable_presentation(
            agent_id=agent_id,
            credential_ids=ids,
            audience_did=audience_did,
        )
        return json.dumps(result, indent=2, default=str)
