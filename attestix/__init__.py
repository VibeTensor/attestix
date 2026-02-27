"""Attestix - Attestation Infrastructure for AI Agents.

This namespace package provides convenient imports for all Attestix modules.
Both import patterns are supported for backward compatibility:

    # Namespaced imports (recommended)
    from attestix.services.identity_service import IdentityService
    from attestix.services.credential_service import CredentialService

    # Flat imports (legacy, still supported)
    from services.identity_service import IdentityService
    from services.credential_service import CredentialService

Modules:
    - attestix.services: Identity, credentials, compliance, delegation, reputation, provenance
    - attestix.tools: MCP tool definitions (47 tools across 9 modules)
    - attestix.auth: Cryptographic utilities (Ed25519, SSRF protection)
    - attestix.blockchain: Merkle trees and EAS anchoring
"""

__version__ = "0.2.3"

# Re-export submodules for convenient access
from attestix import services
from attestix import tools
from attestix import auth
from attestix import blockchain

__all__ = [
    "__version__",
    "services",
    "tools",
    "auth",
    "blockchain",
]
