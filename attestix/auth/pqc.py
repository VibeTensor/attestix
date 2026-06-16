"""Post-quantum and hybrid signing for Attestix (FIPS 204 ML-DSA-65).

OPTIONAL module. It requires the ``[pqc]`` extra (``pip install attestix[pqc]``),
which pulls in ``dilithium-py`` (a pure-Python ML-DSA implementation, so it adds
no native-build burden and keeps the verifier portable). The classical Ed25519
path in :mod:`attestix.auth.crypto` is unchanged and remains the default; nothing
here touches it.

What this adds, additively:

- **ML-DSA-65** (FIPS 204) sign / verify over the same JCS canonical form the
  Ed25519 path uses, so the signed bytes are identical across suites.
- A **hybrid composite** (Ed25519 + ML-DSA-65) where a verifier MUST validate
  BOTH signatures. This "weak non-separability" defeats signature stripping: an
  attacker who breaks one algorithm still cannot forge a valid composite, and a
  downgrade to the classical-only half is rejected. It mirrors the IETF
  composite-signature and W3C ``di-quantum-safe`` direction, letting Attestix
  issue classical-today / quantum-safe-tomorrow credentials without re-issuing
  identities ("harvest-now, decrypt-later" does not touch a hybrid attestation).
- ``did:key`` Multikey encoding for ML-DSA-65 (multicodec ``0x1211``).

Cryptosuite identifiers (for Data Integrity proofs and conformance vectors):

- ``mldsa65-jcs-2026``                 : pure ML-DSA-65.
- ``hybrid-ed25519-mldsa65-jcs-2026``  : Ed25519 + ML-DSA-65 composite.
"""
from __future__ import annotations

import base64
from typing import Tuple

import base58
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from attestix.auth.crypto import (
    canonicalize_json,
    sign_json_payload,
    verify_json_signature,
)

SUITE_MLDSA65 = "mldsa65-jcs-2026"
SUITE_HYBRID = "hybrid-ed25519-mldsa65-jcs-2026"

# Multicodec code 0x1211 (ml-dsa-65-pub) encoded as an unsigned LEB128 varint.
MLDSA65_MULTICODEC_PREFIX = bytes([0x91, 0x24])

# Separator between the two halves of a hybrid proof value. Chosen because it is
# absent from both the base64url and standard-base64 alphabets, so it can never
# collide with either signature encoding.
_HYBRID_SEP = "~"


def _ml_dsa():
    """Return the ML-DSA-65 implementation, or raise a clear install hint."""
    try:
        from dilithium_py.ml_dsa import ML_DSA_65

        return ML_DSA_65
    except ImportError as exc:  # pragma: no cover - exercised only without the extra
        raise ImportError(
            "Post-quantum signing requires the [pqc] extra: "
            "pip install attestix[pqc]"
        ) from exc


def _b64u(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64u_decode(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def generate_mldsa_keypair() -> Tuple[bytes, bytes]:
    """Generate an ML-DSA-65 keypair. Returns ``(public_bytes, secret_bytes)``."""
    public_key, secret_key = _ml_dsa().keygen()
    return public_key, secret_key


def mldsa_sign(secret_key: bytes, payload: dict) -> str:
    """Sign ``payload`` (JCS-canonicalized) with ML-DSA-65; return base64url."""
    signature = _ml_dsa().sign(secret_key, canonicalize_json(payload))
    return _b64u(signature)


def mldsa_verify(public_key: bytes, payload: dict, signature_b64: str) -> bool:
    """Verify an ML-DSA-65 signature over the canonical ``payload``."""
    try:
        return bool(
            _ml_dsa().verify(
                public_key, canonicalize_json(payload), _b64u_decode(signature_b64)
            )
        )
    except Exception:
        return False


def hybrid_sign(
    ed_private: Ed25519PrivateKey, mldsa_secret: bytes, payload: dict
) -> str:
    """Produce a composite Ed25519 + ML-DSA-65 proof value: ``<ed>~<mldsa>``.

    Both halves sign the SAME JCS-canonical bytes of ``payload``.
    """
    ed_sig = sign_json_payload(ed_private, payload)
    pq_sig = mldsa_sign(mldsa_secret, payload)
    return f"{ed_sig}{_HYBRID_SEP}{pq_sig}"


def hybrid_verify(
    ed_public: Ed25519PublicKey,
    mldsa_public: bytes,
    payload: dict,
    proof_value: str,
) -> bool:
    """Verify a composite proof. BOTH signatures MUST validate (anti-stripping).

    Returns False if either half is missing, malformed, or invalid, so a proof
    cannot be downgraded to a single algorithm.
    """
    if _HYBRID_SEP not in proof_value:
        return False
    ed_sig, _, pq_sig = proof_value.partition(_HYBRID_SEP)
    if not ed_sig or not pq_sig:
        return False
    return verify_json_signature(ed_public, payload, ed_sig) and mldsa_verify(
        mldsa_public, payload, pq_sig
    )


def mldsa_public_key_to_did_key(public_key: bytes) -> str:
    """did:key for an ML-DSA-65 public key (multicodec 0x1211 + base58btc)."""
    encoded = base58.b58encode(MLDSA65_MULTICODEC_PREFIX + public_key).decode("ascii")
    return f"did:key:z{encoded}"


def did_key_to_mldsa_public_key(did: str) -> bytes:
    """Extract the ML-DSA-65 public key bytes from an ML-DSA ``did:key``."""
    if not did.startswith("did:key:z"):
        raise ValueError(f"Invalid did:key format: {did}")
    decoded = base58.b58decode(did[len("did:key:z"):])
    if decoded[: len(MLDSA65_MULTICODEC_PREFIX)] != MLDSA65_MULTICODEC_PREFIX:
        raise ValueError("Not an ML-DSA-65 did:key (wrong multicodec prefix)")
    return decoded[len(MLDSA65_MULTICODEC_PREFIX):]
