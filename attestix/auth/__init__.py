"""Attestix auth - re-exports from flat module for namespace compatibility.

Modules:
    - crypto: Ed25519 key management, signing, verification
    - ssrf: SSRF protection for outbound HTTP requests
    - token_parser: Identity token parsing utilities
"""

# Re-export all from the flat auth module
from auth.crypto import (
    generate_ed25519_keypair,
    load_or_create_signing_key,
    private_key_to_bytes,
    public_key_to_bytes,
    private_key_from_bytes,
    public_key_from_bytes,
    public_key_to_did_key,
    did_key_to_public_key,
    did_key_fragment,
    sign_json_payload,
    verify_json_signature,
    sign_message,
    verify_signature,
    canonicalize_json,
)

from auth.ssrf import validate_url_host

from auth.token_parser import extract_identity_from_token

# Re-export submodules as relative imports for consistent module identity
from . import crypto  # noqa: E402
from . import ssrf  # noqa: E402
from . import token_parser  # noqa: E402

__all__ = [
    # Crypto functions
    "generate_ed25519_keypair",
    "load_or_create_signing_key",
    "private_key_to_bytes",
    "public_key_to_bytes",
    "private_key_from_bytes",
    "public_key_from_bytes",
    "public_key_to_did_key",
    "did_key_to_public_key",
    "did_key_fragment",
    "sign_json_payload",
    "verify_json_signature",
    "sign_message",
    "verify_signature",
    "canonicalize_json",
    # SSRF
    "validate_url_host",
    # Token parser
    "extract_identity_from_token",
    # Submodules
    "crypto",
    "ssrf",
    "token_parser",
]
