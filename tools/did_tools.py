"""DID operation MCP tools for Attestix (3 tools)."""

import json


def register(mcp):
    """Register DID tools with the MCP server."""

    @mcp.tool()
    async def resolve_did(did: str) -> str:
        """Resolve any DID to its DID Document.

        Supports did:key (local), did:web (HTTP), and others via Universal Resolver.

        Args:
            did: The DID to resolve (e.g., did:key:z6Mk..., did:web:example.com).
        """
        from services.cache import get_service
        from services.did_service import DIDService

        svc = get_service(DIDService)
        result = svc.resolve_did(did)
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def create_did_key() -> str:
        """Generate an ephemeral did:key identity with an Ed25519 keypair.

        Returns the DID, DID Document, and keypair (store private key securely).
        """
        from services.cache import get_service
        from services.did_service import DIDService

        svc = get_service(DIDService)
        result = svc.create_did_key()
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def create_did_web(domain: str, path: str = "") -> str:
        """Generate a did:web DID Document for self-hosting.

        You must host the returned document at the specified URL for the DID to be resolvable.

        Args:
            domain: The domain name (e.g., vibetensor.com).
            path: Optional path segment (e.g., agents/mybot).
        """
        from services.cache import get_service
        from services.did_service import DIDService

        svc = get_service(DIDService)
        result = svc.create_did_web(domain, path)
        return json.dumps(result, indent=2, default=str)
