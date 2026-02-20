"""Delegation MCP tools for Attestix (3 tools)."""

import json
from typing import Optional


def register(mcp):
    """Register delegation tools with the MCP server."""

    @mcp.tool()
    async def create_delegation(
        issuer_agent_id: str,
        audience_agent_id: str,
        capabilities: str,
        expiry_hours: int = 24,
    ) -> str:
        """Create a UCAN-style delegation token granting capabilities from one agent to another.

        Args:
            issuer_agent_id: The agent granting capabilities (Attestix agent ID).
            audience_agent_id: The agent receiving capabilities (Attestix agent ID).
            capabilities: Comma-separated list of capabilities to delegate.
            expiry_hours: Hours until the delegation expires (default 24).
        """
        from services.cache import get_service
        from services.delegation_service import DelegationService

        svc = get_service(DelegationService)
        caps = [c.strip() for c in capabilities.split(",") if c.strip()]
        result = svc.create_delegation(
            issuer_agent_id=issuer_agent_id,
            audience_agent_id=audience_agent_id,
            capabilities=caps,
            expiry_hours=expiry_hours,
        )
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def verify_delegation(token: str) -> str:
        """Verify a UCAN delegation token's signature, expiry, and structure.

        Args:
            token: The JWT delegation token to verify.
        """
        from services.cache import get_service
        from services.delegation_service import DelegationService

        svc = get_service(DelegationService)
        result = svc.verify_delegation(token)
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def revoke_delegation(jti: str, reason: str = "") -> str:
        """Revoke a UCAN delegation token by its JTI (JWT ID).

        Once revoked, the token will fail verification even if not expired.

        Args:
            jti: The unique identifier of the delegation (from create_delegation response).
            reason: Why this delegation is being revoked.
        """
        from services.cache import get_service
        from services.delegation_service import DelegationService

        svc = get_service(DelegationService)
        result = svc.revoke_delegation(jti=jti, reason=reason)
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def list_delegations(
        agent_id: str = "",
        role: str = "any",
        include_expired: bool = False,
    ) -> str:
        """List delegation tokens, optionally filtered by agent and role.

        Args:
            agent_id: Filter by agent ID (empty = all).
            role: Filter role: 'issuer', 'audience', or 'any'.
            include_expired: Whether to include expired delegations.
        """
        from services.cache import get_service
        from services.delegation_service import DelegationService

        svc = get_service(DelegationService)
        results = svc.list_delegations(
            agent_id=agent_id or None,
            role=role,
            include_expired=include_expired,
        )
        return json.dumps(results, indent=2, default=str)
