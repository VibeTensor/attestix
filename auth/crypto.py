"""Ed25519 cryptographic operations for Attestix.

Handles key generation, signing, verification, and did:key creation.
"""

import base64
import json
from pathlib import Path
from typing import Optional, Tuple

import base58
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from config import SIGNING_KEY_FILE
from errors import ErrorCategory, log_and_format_error

# Multicodec prefix for Ed25519 public key (0xed 0x01)
ED25519_MULTICODEC_PREFIX = bytes([0xED, 0x01])


def generate_ed25519_keypair() -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """Generate a new Ed25519 keypair."""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


def private_key_to_bytes(private_key: Ed25519PrivateKey) -> bytes:
    """Serialize private key to raw 32-byte seed."""
    return private_key.private_bytes(
        Encoding.Raw, PrivateFormat.Raw, NoEncryption()
    )


def public_key_to_bytes(public_key: Ed25519PublicKey) -> bytes:
    """Serialize public key to raw 32 bytes."""
    return public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)


def private_key_from_bytes(key_bytes: bytes) -> Ed25519PrivateKey:
    """Deserialize private key from raw 32-byte seed."""
    return Ed25519PrivateKey.from_private_bytes(key_bytes)


def public_key_from_bytes(key_bytes: bytes) -> Ed25519PublicKey:
    """Deserialize public key from raw 32 bytes."""
    return Ed25519PublicKey.from_public_bytes(key_bytes)


def sign_message(private_key: Ed25519PrivateKey, message: bytes) -> bytes:
    """Sign a message with Ed25519 private key."""
    return private_key.sign(message)


def verify_signature(
    public_key: Ed25519PublicKey, signature: bytes, message: bytes
) -> bool:
    """Verify an Ed25519 signature. Returns True if valid."""
    try:
        public_key.verify(signature, message)
        return True
    except Exception:
        return False


def public_key_to_did_key(public_key: Ed25519PublicKey) -> str:
    """Convert Ed25519 public key to did:key identifier.

    Format: did:key:z<base58btc(multicodec_prefix + raw_public_key)>
    """
    raw_bytes = public_key_to_bytes(public_key)
    multicodec_bytes = ED25519_MULTICODEC_PREFIX + raw_bytes
    encoded = base58.b58encode(multicodec_bytes).decode("ascii")
    return f"did:key:z{encoded}"


def did_key_to_public_key(did: str) -> Ed25519PublicKey:
    """Extract Ed25519 public key from did:key identifier."""
    if not did.startswith("did:key:z"):
        raise ValueError(f"Invalid did:key format: {did}")

    encoded = did[len("did:key:z"):]
    decoded = base58.b58decode(encoded)

    if not decoded[:2] == ED25519_MULTICODEC_PREFIX:
        raise ValueError(f"Not an Ed25519 did:key (wrong multicodec prefix)")

    raw_public = decoded[2:]
    return public_key_from_bytes(raw_public)


# --- Server signing key management ---

def load_or_create_signing_key(
    key_file: Optional[Path] = None,
) -> Tuple[Ed25519PrivateKey, str]:
    """Load server signing key from file or create a new one.

    Returns (private_key, did_key_string).
    """
    key_path = key_file or SIGNING_KEY_FILE

    if key_path.exists():
        try:
            with open(key_path, "r") as f:
                data = json.load(f)
            priv_bytes = base64.b64decode(data["private_key_b64"])
            private_key = private_key_from_bytes(priv_bytes)
            did = data["did_key"]
            return private_key, did
        except Exception as e:
            log_and_format_error(
                "load_or_create_signing_key", e, ErrorCategory.CRYPTO,
                user_message="Corrupted signing key file, generating new key",
            )

    # Generate new keypair
    private_key, public_key = generate_ed25519_keypair()
    did = public_key_to_did_key(public_key)

    key_data = {
        "did_key": did,
        "private_key_b64": base64.b64encode(
            private_key_to_bytes(private_key)
        ).decode("ascii"),
        "algorithm": "Ed25519",
        "note": "Attestix server signing key. Do NOT share.",
    }

    with open(key_path, "w") as f:
        json.dump(key_data, f, indent=2)

    return private_key, did


def _normalize_for_signing(obj):
    """Recursively normalize all strings to NFC Unicode form for consistent signing."""
    import unicodedata
    if isinstance(obj, str):
        return unicodedata.normalize("NFC", obj)
    elif isinstance(obj, dict):
        return {_normalize_for_signing(k): _normalize_for_signing(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_normalize_for_signing(x) for x in obj]
    return obj


def sign_json_payload(private_key: Ed25519PrivateKey, payload: dict) -> str:
    """Sign a JSON payload (canonical NFC-normalized form) and return base64url signature."""
    normalized = _normalize_for_signing(payload)
    canonical = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    sig_bytes = sign_message(private_key, canonical.encode("utf-8"))
    return base64.urlsafe_b64encode(sig_bytes).decode("ascii")


def verify_json_signature(
    public_key: Ed25519PublicKey, payload: dict, signature_b64: str
) -> bool:
    """Verify a JSON payload signature."""
    normalized = _normalize_for_signing(payload)
    canonical = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    sig_bytes = base64.urlsafe_b64decode(signature_b64)
    return verify_signature(public_key, sig_bytes, canonical.encode("utf-8"))
