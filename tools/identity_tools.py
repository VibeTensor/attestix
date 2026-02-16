"""Identity management MCP tools for AURA Protocol (7 tools)."""

import json
from typing import Optional


def _validate_required(params: dict) -> str:
    """Return error JSON if any required param is empty, else empty string."""
    for name, value in params.items():
        if not value or (isinstance(value, str) and not value.strip()):
            return json.dumps({"error": f"{name} cannot be empty"})
    return ""


def register(mcp):
    """Register identity tools with the MCP server."""

    @mcp.tool()
    async def create_agent_identity(
        display_name: str,
        source_protocol: str = "manual",
        identity_token: str = "",
        capabilities: str = "",
        description: str = "",
        issuer_name: str = "",
        expiry_days: int = 365,
    ) -> str:
        """Create a Unified Agent Identity Token (UAIT) from any identity source.

        Args:
            display_name: Human-readable name for the agent.
            source_protocol: Origin protocol (mcp_oauth, a2a, did, api_key, manual).
            identity_token: The original token/DID/URL (optional).
            capabilities: Comma-separated list of capabilities.
            description: What this agent does.
            issuer_name: Who issued this identity.
            expiry_days: Days until expiry (default 365).
        """
        err = _validate_required({"display_name": display_name})
        if err:
            return err

        from services.cache import get_service
        from services.identity_service import IdentityService

        svc = get_service(IdentityService)
        caps = [c.strip() for c in capabilities.split(",") if c.strip()] if capabilities else []
        result = svc.create_identity(
            display_name=display_name,
            source_protocol=source_protocol,
            identity_token=identity_token,
            capabilities=caps,
            description=description,
            issuer_name=issuer_name,
            expiry_days=expiry_days,
        )
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def resolve_identity(identity_token: str) -> str:
        """Auto-detect token type (JWT/DID/URL/API key) and create a UAIT.

        Args:
            identity_token: Any identity string to analyze and register.
        """
        from auth.token_parser import extract_identity_from_token
        from services.cache import get_service
        from services.identity_service import IdentityService

        token_info = extract_identity_from_token(identity_token)
        svc = get_service(IdentityService)
        result = svc.create_identity(
            display_name=f"Resolved-{token_info['token_type']}",
            source_protocol=token_info["token_type"],
            identity_token=identity_token,
        )
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def verify_identity(agent_id: str) -> str:
        """Verify a UAIT: check existence, revocation, expiry, and signature.

        Args:
            agent_id: The AURA agent ID (e.g., aura:abc123...).
        """
        from services.cache import get_service
        from services.identity_service import IdentityService

        svc = get_service(IdentityService)
        result = svc.verify_identity(agent_id)
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def translate_identity(
        agent_id: str,
        target_format: str = "summary",
    ) -> str:
        """Convert a UAIT to another identity format.

        Args:
            agent_id: The AURA agent ID to translate.
            target_format: One of: a2a_agent_card, did_document, oauth_claims, summary.
        """
        from services.cache import get_service
        from services.identity_service import IdentityService

        svc = get_service(IdentityService)
        result = svc.translate_identity(agent_id, target_format)
        if result is None:
            return json.dumps({"error": f"Agent {agent_id} not found"})
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def list_identities(
        source_protocol: str = "",
        include_revoked: bool = False,
        limit: int = 50,
    ) -> str:
        """List all registered agent identities (UAITs).

        Args:
            source_protocol: Filter by protocol (mcp_oauth, a2a, did, api_key, manual). Empty = all.
            include_revoked: Whether to include revoked identities.
            limit: Maximum number of results.
        """
        from services.cache import get_service
        from services.identity_service import IdentityService

        svc = get_service(IdentityService)
        results = svc.list_identities(
            source_protocol=source_protocol or None,
            include_revoked=include_revoked,
            limit=limit,
        )
        return json.dumps(results, indent=2, default=str)

    @mcp.tool()
    async def get_identity(agent_id: str) -> str:
        """Get full UAIT details for a specific agent.

        Args:
            agent_id: The AURA agent ID.
        """
        from services.cache import get_service
        from services.identity_service import IdentityService

        svc = get_service(IdentityService)
        result = svc.get_identity(agent_id)
        if result is None:
            return json.dumps({"error": f"Agent {agent_id} not found"})
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def revoke_identity(agent_id: str, reason: str = "") -> str:
        """Revoke a UAIT, marking it as no longer valid.

        Args:
            agent_id: The AURA agent ID to revoke.
            reason: Why this identity is being revoked.
        """
        from services.cache import get_service
        from services.identity_service import IdentityService

        svc = get_service(IdentityService)
        result = svc.revoke_identity(agent_id, reason)
        if result is None:
            return json.dumps({"error": f"Agent {agent_id} not found"})
        return json.dumps({"revoked": True, "agent_id": agent_id, "reason": reason})
