"""Attestix - Attestation Infrastructure for AI Agents.

Canonical, installable namespace package. v0.4.0-rc.2 promoted all source
modules into the ``attestix.*`` namespace so a ``pip install attestix`` wheel
no longer drops flat top-level packages (``services/``, ``auth/``, ``storage/``,
...) into site-packages. The pre-rc.2 flat imports keep working via thin
deprecation shims and are scheduled for removal in v0.5.0.

Canonical import paths (recommended)::

    from attestix.services.identity_service import IdentityService
    from attestix.signing.inprocess_signer import InProcessSigner
    from attestix.auth.crypto import sign_json_payload
    from attestix.storage.repository import Repository
    from attestix.config import DEFAULT_EXPIRY_DAYS, load_identities

Modules:
    - attestix.services: Identity, credentials, compliance, delegation, reputation, provenance
    - attestix.tools: MCP tool definitions (47 tools across 9 modules)
    - attestix.auth: Cryptographic utilities (Ed25519, SSRF protection)
    - attestix.blockchain: Merkle trees and EAS anchoring
    - attestix.storage: Pluggable persistence (Repository seam, file / memory / pg)
    - attestix.signing: Pluggable signing (Signer seam, in-process / kms)
    - attestix.audit: Tamper-evident audit event chain
    - attestix.tenancy: Tenant context / DEFAULT_TENANT
    - attestix.idempotency: Stripe-style idempotency keys + middleware
    - attestix.api: FastAPI REST surface
    - attestix.config: Process configuration and on-disk paths
    - attestix.errors: Centralized error categories and structured logging
"""

__version__ = "0.4.1rc1"

# Re-export submodules for convenient access
from attestix import services
from attestix import tools
from attestix import auth
from attestix import blockchain
from attestix import storage
from attestix import signing
from attestix import audit
from attestix import tenancy
from attestix import idempotency

__all__ = [
    "__version__",
    "services",
    "tools",
    "auth",
    "blockchain",
    "storage",
    "signing",
    "audit",
    "tenancy",
    "idempotency",
]
