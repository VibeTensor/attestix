"""Byte-parity regression: InProcessSigner == v0.3.0 sign_json_payload (SC-005).

The default in-process signer MUST produce signatures byte-identical to the
v0.3.0 path (``sign_json_payload(private_key, payload)``) for the same input.
This locks the default-signer parity guarantee so any future refactor that drifts
the output is caught immediately.

The fixed keypair is generated externally (via ``auth.crypto``) and injected into
``InProcessSigner``, so the test never asks a signer instance to export its
private material — the signer boundary intentionally has no private-key export
path.
"""

from auth.crypto import (
    generate_ed25519_keypair,
    public_key_to_did_key,
    sign_json_payload,
    verify_json_signature,
)
from signing import InProcessSigner


def _fixed_payloads():
    return [
        {},
        {"a": 1},
        {"z": 1, "a": 2, "m": 3},  # key-order independence
        {"unicode": "café", "nested": {"list": [1, 2, {"deep": True}]}},
        {"float_whole": 1.0, "int": 1, "bool": False, "null": None},
    ]


def _injected_signer():
    """Build a signer from an externally generated keypair (no key export)."""
    private_key, public_key = generate_ed25519_keypair()
    did = public_key_to_did_key(public_key)
    return InProcessSigner(private_key=private_key, did=did), private_key


def test_inprocess_signer_byte_identical_to_v030():
    """For a fixed key + fixed input, signer.sign == sign_json_payload(key, ...)."""
    signer, private_key = _injected_signer()

    for payload in _fixed_payloads():
        via_signer = signer.sign(payload)
        via_v030 = sign_json_payload(private_key, payload)
        assert via_signer == via_v030, f"signature drift for payload {payload!r}"


def test_inprocess_signer_self_verifies():
    signer = InProcessSigner()
    for payload in _fixed_payloads():
        sig = signer.sign(payload)
        assert verify_json_signature(signer.public_key(), payload, sig) is True


def test_inprocess_signer_did_matches_loaded_key():
    """The signer's DID must match the loaded key's did:key."""
    from auth.crypto import did_key_to_public_key, public_key_to_bytes

    signer = InProcessSigner()
    derived = did_key_to_public_key(signer.did)
    assert public_key_to_bytes(derived) == public_key_to_bytes(signer.public_key())


def test_inprocess_signer_injected_keypair_is_used():
    """An explicitly injected (private_key, did) pair is used as-is."""
    private_key, public_key = generate_ed25519_keypair()
    did = public_key_to_did_key(public_key)
    injected = InProcessSigner(private_key=private_key, did=did)
    assert injected.did == did
    payload = {"check": "injected"}
    assert injected.sign(payload) == sign_json_payload(private_key, payload)
