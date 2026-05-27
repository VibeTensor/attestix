"""Shared Signer contract suite (v0.4.0, FR-009 / SC-004).

This suite is parametrized over EVERY concrete ``Signer`` implementation: the
default ``InProcessSigner`` and a ``StubKmsSigner`` standing in for a KMS/HSM
backend (live KMS is impractical in CI per the spec Assumptions). Both must pass
identical assertions, enforcing Liskov substitution at the signing boundary and
confirming that an alternative signer's output verifies through the standard
``auth.crypto`` verification path.
"""

import base64

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from auth.crypto import (
    canonicalize_json,
    public_key_to_did_key,
    verify_json_signature,
)
from signing import InProcessSigner, Signer


class StubKmsSigner(Signer):
    """A KMS/HSM stand-in that satisfies the Signer contract.

    It models a backend that signs canonical bytes with an Ed25519 key the engine
    never sees as a class attribute API (the private key is held privately and is
    NOT exposed via any contract method), and exposes only the public key / DID.
    This mirrors how a real ``KmsSigner`` would canonicalize locally then delegate
    the raw-bytes signing to KMS.
    """

    def __init__(self) -> None:
        self.__private = Ed25519PrivateKey.generate()
        self._public = self.__private.public_key()
        self._did = public_key_to_did_key(self._public)

    def sign(self, payload: dict) -> str:
        canonical = canonicalize_json(payload)
        sig = self.__private.sign(canonical)
        return base64.urlsafe_b64encode(sig).decode("ascii")

    def public_key(self) -> Ed25519PublicKey:
        return self._public

    @property
    def did(self) -> str:
        return self._did


SIGNER_FACTORIES = {
    "inprocess": InProcessSigner,
    "stub_kms": StubKmsSigner,
}


@pytest.fixture(params=list(SIGNER_FACTORIES), ids=list(SIGNER_FACTORIES))
def signer(request) -> Signer:
    """A fresh Signer implementation per parametrized run.

    InProcessSigner picks up the temp signing-key path via the autouse
    ``tmp_attestix`` fixture in conftest.
    """
    return SIGNER_FACTORIES[request.param]()


def test_is_signer_subclass(signer):
    assert isinstance(signer, Signer)


def test_signature_verifies_via_standard_path(signer):
    payload = {"hello": "world", "n": 1, "nested": {"a": [1, 2, 3]}}
    sig = signer.sign(payload)
    assert verify_json_signature(signer.public_key(), payload, sig) is True


def test_signature_is_base64url_string(signer):
    sig = signer.sign({"x": 1})
    assert isinstance(sig, str)
    # Round-trips as base64url without error.
    base64.urlsafe_b64decode(sig)


def test_tampered_payload_fails_verification(signer):
    payload = {"amount": 100}
    sig = signer.sign(payload)
    tampered = {"amount": 999}
    assert verify_json_signature(signer.public_key(), tampered, sig) is False


def test_did_is_stable(signer):
    assert signer.did == signer.did


def test_did_matches_public_key(signer):
    # The did:key must encode the same public key the signer discloses.
    from auth.crypto import did_key_to_public_key, public_key_to_bytes

    derived = did_key_to_public_key(signer.did)
    assert public_key_to_bytes(derived) == public_key_to_bytes(signer.public_key())


def test_no_private_key_method_in_contract(signer):
    # The Signer contract exposes no API returning private key bytes.
    for attr in ("private_key", "private_bytes", "private_key_bytes", "secret"):
        assert not hasattr(signer, attr), (
            f"Signer must not expose private material via .{attr}()"
        )
