"""Attestix auth - re-exports from flat module for namespace compatibility.

Modules:
    - crypto: Ed25519 key management, signing, verification
    - ssrf: SSRF protection for outbound HTTP requests
    - token_parser: Identity token parsing utilities
"""

# Re-export all from the flat auth module via relative imports
from .crypto import (
    canonicalize_json,
    did_key_fragment,
    did_key_to_public_key,
    generate_ed25519_keypair,
    load_or_create_signing_key,
    private_key_from_bytes,
    private_key_to_bytes,
    public_key_from_bytes,
    public_key_to_bytes,
    public_key_to_did_key,
    sign_json_payload,
    sign_message,
    verify_json_signature,
    verify_signature,
)

from .ssrf import validate_url_host

from .token_parser import extract_identity_from_token

# Re-export submodules for namespace access
from . import crypto
from . import ssrf
from . import token_parser

__all__ = [
    "canonicalize_json",
    "crypto",
    "did_key_fragment",
    "did_key_to_public_key",
    "extract_identity_from_token",
    "generate_ed25519_keypair",
    "load_or_create_signing_key",
    "private_key_from_bytes",
    "private_key_to_bytes",
    "public_key_from_bytes",
    "public_key_to_bytes",
    "public_key_to_did_key",
    "sign_json_payload",
    "sign_message",
    "ssrf",
    "token_parser",
    "validate_url_host",
    "verify_json_signature",
    "verify_signature",
]
